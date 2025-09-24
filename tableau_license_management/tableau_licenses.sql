create table tableau.licenses.site_roles (
    role_id varchar(50),
    role_name varchar(50)
);

insert into tableau.licenses.site_roles (role_id, role_name) values
('1', 'Administrator Creator'),
('2', 'Administrator Explorer'),
('3', 'Creator'),
('4', 'Explorer (Can Publish)'),
('5', 'Explorer'),
('6', 'Viewer');

create table tableau.licenses.users (
    employee_id varchar(50),
    employee_name varchar(50),
    site_role_id varchar(50),
    site_id int
);

insert into tableau.licenses.users (employee_id, employee_name, site_role_id, site_id) values
-- scranton (site_id = 8)
(100001, 'Michael Scott', '1', 8),
(100002, 'Dwight Schrute', '2', 8),
(100003, 'Jim Halpert', '3', 8),
(100004, 'Pam Beesly', '4', 8),
(100005, 'Ryan Howard', '5', 8),
(100006, 'Kelly Kapoor', '6', 8),
(100007, 'Stanley Hudson', '5', 8),
(100008, 'Angela Martin', '6', 8),
(100009, 'Kevin Malone', '3', 8),
(100010, 'Oscar Martinez', '4', 8),
-- stamford (site_id = 9)
(100011, 'Josh Porter', '1', 9),
(100012, 'Karen Filippelli', '4', 9),
(100013, 'Andy Bernard', '3', 9),
-- utica (site_id = 10)
(100014, 'Craig', '2', 10),
(100015, 'Hannah Smoterich-Barr', '4', 10),
-- nashua (site_id = 11)
(100016, 'Tony Gardner', '3', 11),
(100017, 'Martin Nash', '5', 11);

create table tableau.licenses.org_info (
    employee_id varchar(50),
    employee_name varchar(50),
    department varchar(50),
    active_worker_flag varchar(1)
);

insert into tableau.licenses.org_info (employee_id, employee_name, department, active_worker_flag) values
(100001, 'Michael Scott', 'Management', 'Y'),
(100002, 'Dwight Schrute', 'Sales', 'Y'),
(100003, 'Jim Halpert', 'Sales', 'Y'),
(100004, 'Pam Beesly', 'Reception', 'Y'),
(100005, 'Ryan Howard', 'Temp', 'N'),
(100006, 'Kelly Kapoor', 'Customer Service', 'Y'),
(100007, 'Stanley Hudson', 'Sales', 'Y'),
(100008, 'Angela Martin', 'Accounting', 'Y'),
(100009, 'Kevin Malone', 'Accounting', 'N'),
(100010, 'Oscar Martinez', 'Accounting', 'Y');

create table tableau.licenses.scranton_tableau_org_hist (
    emp_id varchar(50),
    emp_name varchar(50),
    active_worker_flag varchar(1),
    tab_emp_id varchar(50),
    tab_emp_name varchar(50),
    tableau_license varchar(50)
);

-- trigger new employee alert
insert into tableau.licenses.org_info (employee_id, employee_name, department, active_worker_flag)
values ('200001', 'Phyllis Vance', 'Sales', 'Y');

-- trigger departed employee alert
update tableau.licenses.org_info
set active_worker_flag = 'N'
where employee_id = '100002'; -- Dwight Schrute

-- trigger department change alert
update tableau.licenses.org_info
set department = 'Management'
where employee_id = '100003'; -- Jim Halpert

-- trigger license change alert
update tableau.licenses.users
set site_role_id = '1' -- Administrator Creator
where employee_id = '100008'; -- Angela Martin

-- trigger license usage alert
update tableau.licenses.users
set site_role_id = '3' -- Creator
where employee_id in ('100008','100010'); -- Angela Martin & Oscar Martinez