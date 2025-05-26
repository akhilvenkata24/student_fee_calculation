# Student Fee Calculation System

The Student Fee Calculation System is a comprehensive web application designed to manage student admissions, department information, fee structures, and scholarship applications. Built with Flask (Python) backend and MySQL database, it provides a complete solution for educational institutions to handle student financials.

## 🌐 Project Overview
This system simplifies the complex process of student fee management by automating calculations based on department fees, scholarships, and payments. It features a responsive frontend with intuitive forms and real-time status tracking for students and administrators.

## 🎯 Project Objectives
- Streamline student admission and department management
- Automate fee calculations based on department structures
- Manage scholarship applications and fee adjustments
- Track payment history and balances
- Provide real-time status updates for students
- Offer a user-friendly interface for both administrators and students

## 💻 Technologies Used

- **Frontend**:
  - HTML
  - CSS
  - JavaScript

- **Backend**:
  - Python with Flask framework
  - MySQL for database

- **Database**:
  - MySQL (via Flask-MySQLdb)

- **Tools**:
  - Post Man
  - Visual Studio Code(VS Code)
  - GitHub
  - MySQL

## Key Features

### 🏛 Department Management
- Add/update departments with complete fee structure
- Set tuition, lab, library, and transport fees
- Manage seat availability and capacity

### 🎓 Student Admission
- Online application form with department selection
- Temporary ID generation for tracking
- Application status tracking (applied/pending/approved/rejected)

### 💰 Fee Management
- Automatic fee calculation based on department
- Payment recording with multiple methods (Cash, Card, UPI, Bank Transfer)
- Real-time balance tracking
- Payment history view

### 🏆 Scholarship System
- Scholarship creation and management
- Application processing
- Automatic fee adjustment after scholarship approval

### 📊 Status Tracking
- Check application status by ID
- View detailed fee breakdown
- Track payment history and remaining balance

## 🚀 Deployment Guide

### Prerequisites:
- Python 3.x
- MySQL Server
- Flask and required packages (`flask, flask-mysqldb, flask-cors`)

### Steps:

1. **Database Setup**
   - Create database using `crt_db_1.sql`
   - Configure MySQL connection in `app.py`:
     ```python
     app.config['MYSQL_HOST'] = 'localhost'
     app.config['MYSQL_USER'] = 'root'
     app.config['MYSQL_PASSWORD'] = 'root'
     app.config['MYSQL_DB'] = 'db1'
     ```

2. **Backend Setup**
   - Install requirements:
     ```bash
     pip install flask flask-mysqldb flask-cors
     ```
   - Run Flask app:
     ```bash
     python app.py
     ```

3. **Frontend Setup**
   - Open HTML files in browser or deploy to web server
   - All frontend files connect to `http://localhost:5000` by default

4. **Access the System**
   - Start with `index.html` as the main portal
   - Use navigation to access different features

## 📦 Project Structure

- `app.py`: Flask backend with all API endpoints
- `crt_db_1.sql`: Database schema and initial data
- HTML Files:
  - `index.html`: Main portal with navigation
  - `apply.html`: Student admission form
  - `status.html`: Application status checker
  - `balance.html`: Fee payment tracker
  - `apply_scholarship.html`: Scholarship application
  - `scholarships.html`: Scholarship management
  - `add_department.html`: Department management
  - `add_payments.html`: Fee payment recording
  - `update_status.html`: Application status updates

## 🚧 Future Enhancements
- Admin dashboard for comprehensive management
- Email notifications for application updates
- Bulk payment processing
- Financial reports generation
- User authentication and roles
- Mobile app integration

## 👥 Authors
Akhil - 231FA04087, Gowtham - 231FA04094, Neerush - 231FA04109 

B.Tech CSE, VFSTR University
