# Tableau License Monitor – Scranton Site

This project showcases my ability to combine SQL, Python, and automation to solve a real business need.

This Python script tracks changes in employee Tableau licenses for the Scranton branch (site_id = 8). It compares the current day's license assignments and org data to the previous day's snapshot, highlighting changes like:

- ✅ New employees
- ❌ Departures
- 🔁 License role changes
- 🔄 Department changes
- ⚠️ License usage nearing limit

All detected changes are emailed as an HTML-formatted summary. Task scheduler was used to automate the running of this script daily.

---

## 📘 Background 
This script was developed in response to a critical licensing issue. Our organization ran out of Tableau licenses, which prevented new hires from getting access to a critical tool. Additionally, some existing users had their licenses reassigned, even though they were actively using them.

To address this, our department purchased dedicated Tableau licenses for our teams and needed a way to monitor usage closely. This script automates daily comparisons of license assignments, flags approaching usage limits, and detects key license changes.

---

## 🔧 Tools & Technologies
- **Python 3.10+**
- **Pandas** – Data transformation and comparison
- **SQLAlchemy** – SQL connection and execution
- **Gmail SMTP** – For sending automated email reports
- **.env (dotenv)** – For securely storing email credentials
- **SQL Server** – Source for Tableau and organizational data
- **Task Scheduler** – Automation to run the script daily

---

## 📁 Project Structure
- **tableau_license_monitor.py** –  Main script to execute
- **tableau_licenses.sql** –  SQL script to create the databases
- **sql_connection_alchemy.py** –  Database connection logic (not committed to GitHub)
- **.env** –  Environment variables (not committed to GitHub)
- **README.md** –  Project overview and instructions

---

## ⚙️ How It Works
1. SQL query to pull:
    - Tableau license assignments for Scranton (site_id = 8)
    - Org data for Sales and Accounting departments (the departments we purchased licenses for)
2. Compare current and previous snapshots
    - New employees (new ID in today's data)
    - Departures (active_worker_flag = FALSE)
    - License changes (license role changes)
    - Department changes (no longer in Sales or Accounting so don't need one of our licenses)
    - Nearing max allowed licenses (we have 6 Creator and 5 Explorer (Can Publish) licenses)
3. Email a summary of changes using Gmail SMTP
4. Truncate and reload the historical table for tomorrow's comparison

---

## 🚀 Possible Enhancements
- Expand monitoring to include additional Tableau sites or departments
- Integrate with Slack or Teams for real-time notifications
- Add historical trend dashboards for license usage over time
- Implement configurable license thresholds (read from a file or database) instead of hardcoding values
