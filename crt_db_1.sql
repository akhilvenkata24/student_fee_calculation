create database db1;
use db1;

create table departments (
    dept_id int primary key auto_increment,
    dept_name varchar(100) not null unique,
    total_seats int not null,
    available_seats int not null,
    tuition_fee decimal(10, 2) not null,
    lab_fee decimal(10, 2) default 0,
    library_fee decimal(10, 2) default 0,
    transport_fee decimal(10, 2) default 0
);



create table students (
    temp_id int primary key auto_increment,
    name varchar(100) not null,
    dob date not null,
    contact varchar(15),
    applied_department varchar(10),
    status enum('applied', 'pending', 'rejected') default 'applied',
    foreign key (applied_department) references departments(dept_name)
);


create table scholarships (
    scholarship_id int primary key auto_increment,
    name varchar(100) not null,
    description text,
    amount decimal(10, 2) not null,
    eligibility_criteria text
);


create table admissions (
    admission_id int primary key auto_increment,
    temp_id int,
    dept_id int,
    admission_date date not null,
    status enum('approved', 'rejected') default 'approved',
    foreign key (temp_id) references students(temp_id),
    foreign key (dept_id) references departments(dept_id)
);


create table students_approved (
    student_id int primary key auto_increment,
    admission_id int auto_increment,
    name varchar(100) not null,
    dob date not null,
    enrollment_date date not null,
    total_fee decimal(10,2),
    final_fee decimal(10,2)
);

select * from students_approved;
drop table students_approved;
delete from students_approved ;
SET SQL_SAFE_UPDATES = 0;

SET SQL_SAFE_UPDATES = 1;


SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_NAME = 'students_approved'
  AND COLUMN_NAME = 'admission_id'
  AND CONSTRAINT_SCHEMA = 'db1';  -- Replace with your actual database name if different

ALTER TABLE students_approved
ADD final_fee decimal(10,2);


create table scholarships_applied (
    id int primary key auto_increment,
    student_id int,
    scholarship_id int,
    foreign key (student_id) references students_approved(student_id),
    foreign key (scholarship_id) references scholarships(scholarship_id)
);
drop table scholarships_applied;

create table fee_payments (
    payment_id int primary key auto_increment,
    student_id int,
    payment_date date not null,
    payment_method varchar(50),
    total_amount_paid decimal(10, 2) not null,
    remaining_due_after_payment decimal(10, 2),
    foreign key (student_id) references students_approved(student_id)
);

drop table fee_payments;


alter table students
modify status varchar(20) default 'applied';

alter table admissions
modify status varchar(20) default 'approved';


-- Add remaining_due to fee_payments if not already present
alter table fee_payments
add column remaining_due decimal(10,2);

alter table students_approved
add column total_fee decimal(10,2);


select * from departments;

delete from departments where name='Akhil';

select * from students;

delete from students where temp_id=5;

select * from scholarships;

SET SQL_SAFE_UPDATES = 0;

INSERT INTO departments (dept_name, total_seats, available_seats, tuition_fee, lab_fee, library_fee, transport_fee)
VALUES
  ('CSE', 100, 100, 50000.00, 5000.00, 2000.00, 3000.00),
  ('ECE', 80, 80, 45000.00, 4000.00, 2000.00, 3000.00),
  ('MECH', 70, 70, 40000.00, 3000.00, 2000.00, 3000.00),
  ('IT', 90, 90, 48000.00, 5000.00, 2000.00, 3000.00),
  ('BI', 60, 60, 42000.00, 2500.00, 2000.00, 3000.00),
  ('BT', 50, 50, 43000.00, 2500.00, 2000.00, 3000.00),
  ('EEE', 75, 75, 47000.00, 4500.00, 2000.00, 3000.00),
  ('CIVIL', 65, 65, 41000.00, 3500.00, 2000.00, 3000.00);

DESCRIBE students;

ALTER TABLE students 
MODIFY COLUMN status ENUM('applied','pending','rejected','approved') NOT NULL;