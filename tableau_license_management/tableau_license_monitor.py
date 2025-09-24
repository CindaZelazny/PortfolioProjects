"""
Tableau License Monitor for Scranton Site
-----------------------------------------
This script compares current Tableau license assignments and employee data
to the previous day's snapshot. It detects:

- New hires
- Departures
- License changes
- Department changes
- License usage nearing predefined limits

Results are emailed as a formatted HTML report. Can be automated to run daily via task scheduler.

Author: Cinda Zelazny
"""

import os
import smtplib
import pandas as pd

from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy import text

import sql_connection_alchemy as sf  # Custom SQL Server connection module

# Load environment variables (.env stores log in details)
load_dotenv(dotenv_path=r"C:\Users\...\.env")
email_sender = os.getenv('EMAIL_SENDER')
email_password = os.getenv('EMAIL_PASSWORD')

# Create database connection
engine = sf.get_engine()


def send_email(subject, body=None, recipient_list=email_sender):
    """
    Sends an email via Gmail SMTP with an HTML body.
    """
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = email_sender
        msg['To'] = recipient_list
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(email_sender, email_password)
            smtp_server.send_message(msg)

    except Exception as e:
        print(f"Email failed: {e}")


# ------------------------------------------------------------
# STEP 1: Pull current Tableau license data for Scranton site
# ------------------------------------------------------------
tableau_query = """
    SELECT DISTINCT
        u.employee_id AS tab_emp_id,
        u.employee_name AS tab_emp_name,
        r.role_name AS tableau_license
    FROM tableau.licenses.users u
    LEFT JOIN tableau.licenses.site_roles r
        ON r.role_id = u.site_role_id
    WHERE u.site_id = 8
"""
tableau_df = pd.read_sql(tableau_query, con=engine)


# ------------------------------------------------------------
# STEP 2: Pull org data for Sales and Accounting departments
# ------------------------------------------------------------
org_query = """
    SELECT
        employee_id AS emp_id,
        employee_name AS emp_name,
        active_worker_flag
    FROM tableau.licenses.org_info
    WHERE department IN ('Sales', 'Accounting')
"""
org_df = pd.read_sql(org_query, con=engine)


# ------------------------------------------------------------
# STEP 3: Merge org and Tableau data into single current snapshot
# ------------------------------------------------------------
df_today = pd.merge(org_df, tableau_df, how='left', left_on='emp_id', right_on='tab_emp_id')


# ------------------------------------------------------------
# STEP 4: Compare with previous day's snapshot
# ------------------------------------------------------------
# Load previous data
previous_query = "SELECT * FROM tableau.licenses.scranton_tableau_org_hist"
df_previous = pd.read_sql(previous_query, con=engine)

# License limits (adjust as needed)
license_limits = {
    'Creator': 6,
    'Explorer (Can Publish)': 5
}
# Count current usage
license_count = df_today['tableau_license'].value_counts()
# Flag if usage is within 3 of the max allowed
warning_licenses = {
    lic: count
    for lic, count in license_count.items()
    if lic in license_limits and (license_limits[lic] - count) <= 3
}

# Standardize missing values
df_today = df_today.fillna('MISSING')
df_previous = df_previous.fillna('MISSING')

# Merge datasets for change detection
merged = df_previous.merge(df_today, how='left', on='emp_id', suffixes=('_prev', '_today'))
merged = merged.fillna('MISSING')


# ------------------------------------------------------------
# STEP 5: Identify changes between yesterday and today
# ------------------------------------------------------------
new_employees = df_today[~df_today['emp_id'].isin(df_previous['emp_id'])]

departed_employees = merged[
    (merged['active_worker_flag_prev'] == "Y") &
    (merged['active_worker_flag_today'] == "N")
]

department_change_employees = df_previous[~df_previous['emp_id'].isin(df_today['emp_id'])]

license_changes = merged[
    merged['tableau_license_prev'] != merged['tableau_license_today']
]


# ------------------------------------------------------------
# STEP 6: Compose and send HTML summary email if changes found
# ------------------------------------------------------------
def styled_table(df):
    html = '<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; margin-left:0;">'
    # Header row
    html += '<tr style="background-color:#f2f2f2;">'
    for col in df.columns:
        html += f'<th style="border:1px solid black; text-align:center; padding:6px; white-space:nowrap;">{col}</th>'
    html += '</tr>'
    # Data rows
    for _, row in df.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td style="border:1px solid black; text-align:center; padding:6px; white-space:nowrap;">{val}</td>'
        html += '</tr>'
    html += '</table>'
    return html

message = ""

if not new_employees.empty:
    message += '<h3>New Employees:</h3>' + styled_table(
        new_employees[['emp_id', 'emp_name', 'tableau_license']]
    )

if not departed_employees.empty:
    message += '<h3>Departed Employees:</h3>' + styled_table(
        departed_employees[['emp_id', 'emp_name_prev',
                            'active_worker_flag_prev', 'active_worker_flag_today']]
    )

if not department_change_employees.empty:
    message += '<h3>Department Changes:</h3>' + styled_table(
        department_change_employees[['emp_id', 'emp_name', 'tableau_license']]
    )

if not license_changes.empty:
    message += '<h3>License Changes:</h3>' + styled_table(
        license_changes[['emp_id', 'emp_name_prev', 'tableau_license_prev',
                         'emp_name_today', 'tableau_license_today']]
    )

if warning_licenses:
    warning_msg = '<h3>License Count Warning</h3>' + styled_table(
        pd.DataFrame([
            {
                "License": lic,
                "In Use": count,
                "Total Allowed": license_limits[lic],
                "Remaining": license_limits[lic] - count
            }
            for lic, count in warning_licenses.items()
        ])
    )
    message += warning_msg

# Send results if there were any updates
if message:
    send_email(subject='Employee changes detected', body=message)
    print('Changes detected. Please review email for details.')
else: print('No changes detected.')

# ------------------------------------------------------------
# STEP 7: Update historical snapshot with today's data
# ------------------------------------------------------------
# Clear previous snapshot before inserting today’s data
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE tableau.licenses.scranton_tableau_org_hist"))

df_today.to_sql(
    name='scranton_tableau_org_hist',
    con=engine,
    schema='licenses',
    if_exists='append', # Append to allow time travel on table, if needed
    index=False
)
