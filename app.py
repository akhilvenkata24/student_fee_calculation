from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'db1'

mysql = MySQL(app)


# 1. Departments Routes

@app.route('/departments', methods=['GET'])
def get_departments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM departments")
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    result = [dict(zip(col_names, row)) for row in rows]
    return jsonify(result)

@app.route('/departments', methods=['POST'])
def add_department():
    data = request.json
    dept_name = data.get('dept_name')
    tuition_fee = data.get('tuition_fee', 0)
    lab_fee = data.get('lab_fee', 0)
    library_fee = data.get('library_fee', 0)
    transport_fee = data.get('transport_fee', 0)
    total_seats = data.get('total_seats', 0)
    available_seats = data.get('available_seats', total_seats)

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO departments (dept_name, tuition_fee, lab_fee, library_fee, transport_fee, total_seats, available_seats)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (dept_name, tuition_fee, lab_fee, library_fee, transport_fee, total_seats, available_seats))
    mysql.connection.commit()
    return jsonify({"message": "Department added"})

@app.route('/departments/<string:dept_name>', methods=['PUT'])
def update_department(dept_name):
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE departments SET
            tuition_fee=%s, lab_fee=%s, library_fee=%s, transport_fee=%s,
            total_seats=%s, available_seats=%s
        WHERE dept_name=%s
    """, (
        data.get('tuition_fee'), data.get('lab_fee'), data.get('library_fee'), data.get('transport_fee'),
        data.get('total_seats'), data.get('available_seats'), dept_name
    ))
    mysql.connection.commit()
    return jsonify({"message": "Department updated"})

# 2. Students Table (applicants)

@app.route('/students', methods=['GET'])
def get_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]
    return jsonify(result)

@app.route('/students/<int:temp_id>', methods=['GET'])
def get_student(temp_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students WHERE temp_id = %s", (temp_id,))
    row = cur.fetchone()
    if row:
        cols = [desc[0] for desc in cur.description]
        result = dict(zip(cols, row))
        return jsonify(result)
    else:
        return jsonify({"message": "Student not found"})

@app.route('/students', methods=['POST'])
def add_student():
    data = request.json
    name = data.get('name')
    dob = data.get('dob')
    contact = data.get('contact')
    applied_department = data.get('applied_department')
    status = data.get('status', 'applied')

    if not name or not dob or not contact or not applied_department:
        return jsonify({"message": "Missing required fields"}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM departments WHERE dept_name = %s", (applied_department,))
    if cur.fetchone() is None:
        return jsonify({"message": "Invalid department name"}), 400

    cur.execute("""
        SELECT 1 FROM students WHERE name = %s AND dob = %s AND contact = %s
    """, (name, dob, contact))
    if cur.fetchone():
        return jsonify({"message": "Duplicate student entry"}), 409

    cur.execute("""
        INSERT INTO students (name, dob, contact, applied_department, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, dob, contact, applied_department, status))
    mysql.connection.commit()

    temp_id = cur.lastrowid
    return jsonify({"message": "Student application added", "temp_id": temp_id}), 201


@app.route('/students/<int:temp_id>', methods=['PATCH'])
def update_student_status(temp_id):
    try:
        data = request.json
        new_status = data.get('status')
        print(f"Attempting to update status to: {new_status}")
        
        if new_status not in ['applied', 'pending', 'rejected', 'approved']:
            return jsonify({"message": "Invalid status"}), 400
            
        cur = mysql.connection.cursor()
        
        try:
            if new_status == 'approved':
                print("Status is approved, fetching student...")
                # Check if student is already in approved table
                cur.execute("SELECT 1 FROM students_approved WHERE admission_id=%s", (temp_id,))
                if cur.fetchone():
                    return jsonify({"message": "Student is already approved and exists in approved table"}), 400
                
                # Get student details
                cur.execute("""
                    SELECT name, dob, applied_department, status 
                    FROM students 
                    WHERE temp_id=%s
                """, (temp_id,))
                student = cur.fetchone()
                
                if not student:
                    return jsonify({"message": "Student not found"}), 404
                    
                name, dob, applied_department, current_status = student
                print(f"Current status: {current_status}, Applied Department: {applied_department}")
                
                if current_status == 'approved':
                    return jsonify({"message": "Student is already approved in students table"}), 400
                    
                # Fetch department details
                cur.execute("""
                    SELECT dept_id, available_seats, tuition_fee, lab_fee, library_fee, transport_fee 
                    FROM departments 
                    WHERE dept_name=%s
                """, (applied_department,))
                dept = cur.fetchone()
                
                if not dept:
                    return jsonify({"message": "Department not found"}), 404
                    
                dept_id, available_seats, tuition_fee, lab_fee, library_fee, transport_fee = dept
                print(f"Available seats: {available_seats}")
                
                if available_seats <= 0:
                    return jsonify({"message": "No seats available in this department"}), 400
                    
                # Update student status
                cur.execute("UPDATE students SET status=%s WHERE temp_id=%s", (new_status, temp_id))
                print(f"Rows affected by student update: {cur.rowcount}")
                
                # Update department seats
                cur.execute("UPDATE departments SET available_seats = available_seats - 1 WHERE dept_id=%s", (dept_id,))
                print(f"Rows affected by department update: {cur.rowcount}")
                
                # Calculate fees
                total_fee = float(tuition_fee or 0) + float(lab_fee or 0) + float(library_fee or 0) + float(transport_fee or 0)
                final_fee = total_fee
                
                # Format dates
                if isinstance(dob, str):
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                enrollment_date = datetime.now().date()
                
                # Insert into approved table
                cur.execute("""
                    INSERT INTO students_approved (admission_id, name, dob, enrollment_date, total_fee, final_fee)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (temp_id, name, dob, enrollment_date, total_fee, final_fee))
                print(f"Rows inserted into approved table: {cur.rowcount}")
                
                mysql.connection.commit()
                print("Approval successful")
                return jsonify({
                    "message": "Student approved and added to students_approved",
                    "total_fee": total_fee,
                    "final_fee": final_fee
                })
            else:
                print("Updating to non-approved status")
                cur.execute("UPDATE students SET status=%s WHERE temp_id=%s", (new_status, temp_id))
                print(f"Rows affected: {cur.rowcount}")
                mysql.connection.commit()
                return jsonify({"message": "Student status updated"})
                
        finally:
            cur.close()
            
    except Exception as e:
        mysql.connection.rollback()
        print(f"ERROR OCCURRED: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "message": "Internal server error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
# 3. Scholarships Table

@app.route('/scholarships', methods=['GET'])
def get_scholarships():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM scholarships")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]
    return jsonify(result)

@app.route('/scholarships', methods=['POST'])
def add_scholarship():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    amount = data.get('amount')
    eligibility_criteria = data.get('eligibility_criteria')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO scholarships (name, description, amount, eligibility_criteria)
        VALUES (%s, %s, %s, %s)
    """, (name, description, amount, eligibility_criteria))
    mysql.connection.commit()
    return jsonify({"message": "Scholarship added"})

# 4. Removed Admissions Table & Routes

# 5. Students_Approved Table

@app.route('/students_approved', methods=['GET'])
def get_students_approved():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students_approved")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]
    return jsonify(result)

# 6. Scholarships Applied Table

@app.route('/scholarships_applied', methods=['GET'])
def get_scholarships_applied():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM scholarships_applied")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]
    return jsonify(result)

@app.route('/scholarships_applied', methods=['POST'])
def apply_scholarship():
    data = request.json
    student_id = data.get('student_id')  # students_approved.id
    scholarship_id = data.get('scholarship_id')

    if not student_id or not scholarship_id:
        return jsonify({"message": "Missing required fields"}), 400

    cur = mysql.connection.cursor()

    # Check if student exists in students_approved
    cur.execute("SELECT final_fee FROM students_approved WHERE student_id=%s", (student_id,))
    student = cur.fetchone()
    if not student:
        return jsonify({"message": "Approved student not found"}), 404
    current_final_fee = float(student[0])

    # Get scholarship amount
    cur.execute("SELECT amount FROM scholarships WHERE scholarship_id=%s", (scholarship_id,))
    scholarship = cur.fetchone()
    if not scholarship:
        return jsonify({"message": "Scholarship not found"}), 404
    amount = float(scholarship[0])

    # Insert scholarship application
    cur.execute("""
        INSERT INTO scholarships_applied (student_id, scholarship_id)
        VALUES (%s, %s)
    """, (student_id, scholarship_id))

    # Deduct scholarship amount from final_fee (do not allow negative fee)
    new_final_fee = max(0, current_final_fee - amount)
    cur.execute("UPDATE students_approved SET final_fee=%s WHERE student_id=%s", (new_final_fee, student_id))

    mysql.connection.commit()
    return jsonify({"message": "Scholarship applied", "new_final_fee": new_final_fee})


@app.route('/fee_payments', methods=['POST'])
def add_fee_payment():
    data = request.json
    student_id = data.get('student_id')
    amount_paid = data.get('amount_paid')
    payment_method = data.get('payment_method')  # new field
    payment_date = datetime.now().strftime('%Y-%m-%d')

    if not student_id or amount_paid is None or not payment_method:
        return jsonify({"message": "Missing fields"}), 400

    cur = mysql.connection.cursor()

    # Check if the student exists
    cur.execute("SELECT final_fee FROM students_approved WHERE student_id = %s", (student_id,))
    student = cur.fetchone()
    if not student:
        return jsonify({"message": "Student not found"}), 404
    final_fee = float(student[0])

    # Calculate total paid so far
    cur.execute("SELECT COALESCE(SUM(total_amount_paid), 0) FROM fee_payments WHERE student_id = %s", (student_id,))
    total_paid = float(cur.fetchone()[0])

    new_total = total_paid + float(amount_paid)
    balance_due = final_fee - new_total

    if new_total > final_fee:
        return jsonify({"message": "Payment exceeds total fee"}), 400

    # Insert the payment with remaining_due_after_payment
    cur.execute("""
        INSERT INTO fee_payments (student_id, payment_date, payment_method, total_amount_paid, remaining_due_after_payment)
        VALUES (%s, %s, %s, %s, %s)
    """, (student_id, payment_date, payment_method, amount_paid, balance_due))

    mysql.connection.commit()

    return jsonify({
        "message": "Payment recorded successfully",
        "total_paid": new_total,
        "balance_due": balance_due
    })


@app.route('/fee_payments/<int:student_id>', methods=['GET'])
def get_fee_payments(student_id):
    cur = mysql.connection.cursor()

    # Check if the student exists
    cur.execute("SELECT name FROM students_approved WHERE student_id = %s", (student_id,))
    student = cur.fetchone()
    if not student:
        return jsonify({"message": "Student not found"}), 404

    # Fetch all payments for this student
    cur.execute("""
        SELECT payment_id, payment_date, payment_method, total_amount_paid, remaining_due_after_payment
        FROM fee_payments
        WHERE student_id = %s
        ORDER BY payment_date ASC
    """, (student_id,))
    payments = cur.fetchall()

    # Format the response
    payment_list = []
    for row in payments:
        payment_list.append({
            "payment_id": row[0],
            "payment_date": row[1],
            "payment_method": row[2],
            "amount_paid": float(row[3]),
            "remaining_due_after_payment": float(row[4])
        })

    return jsonify({
        "student_id": student_id,
        "student_name": student[0],
        "payments": payment_list
    })




@app.route('/status/<int:temp_id>', methods=['GET'])
def get_student_status(temp_id):
    cur = mysql.connection.cursor()
    
    # Get basic student info
    cur.execute("""
        SELECT s.temp_id, s.name, s.status, s.applied_department
        FROM students s
        WHERE s.temp_id = %s
    """, (temp_id,))
    student = cur.fetchone()
    
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    # Basic response structure
    response = {
        "temp_id": student[0],
        "name": student[1],
        "status": student[2],
        "applied_department": student[3]
    }
    
    if student[2] == 'approved':
        # Get detailed fee info from departments
        cur.execute("""
            SELECT d.tuition_fee, d.lab_fee, d.library_fee, d.transport_fee
            FROM departments d
            WHERE d.dept_name = %s
        """, (student[3],))
        fee_info = cur.fetchone()
        
        if fee_info:
            response.update({
                "tuition_fee": float(fee_info[0]),
                "lab_fee": float(fee_info[1]),
                "library_fee": float(fee_info[2]),
                "transport_fee": float(fee_info[3])
            })
        
        # Get approved student details
        cur.execute("""
            SELECT sa.student_id, sa.final_fee
            FROM students_approved sa
            WHERE sa.admission_id = %s
        """, (temp_id,))
        approved_info = cur.fetchone()
        
        if approved_info:
            response.update({
                "student_id": approved_info[0],
                "final_fee": float(approved_info[1])
            })
        
        # Get any applied scholarships
        if approved_info:  # Only if student is in students_approved
            cur.execute("""
                SELECT SUM(s.amount) as total_scholarship
                FROM scholarships_applied sa
                JOIN scholarships s ON sa.scholarship_id = s.scholarship_id
                WHERE sa.student_id = %s
            """, (approved_info[0],))
            scholarship = cur.fetchone()
            
            if scholarship and scholarship[0]:
                response["scholarship"] = float(scholarship[0])
    
    return jsonify(response)




@app.route('/status/student/<int:student_id>', methods=['GET'])
def get_student_status_by_student_id(student_id):
    cur = mysql.connection.cursor()

    # Get approved student info (joined with students table for name, dept, status)
    cur.execute("""
        SELECT sa.student_id, s.name, s.status, s.applied_department, sa.final_fee
        FROM students_approved sa
        JOIN students s ON sa.admission_id = s.temp_id
        WHERE sa.student_id = %s
    """, (student_id,))
    student = cur.fetchone()

    if not student:
        return jsonify({"message": "Student not found"}), 404

    response = {
        "student_id": student[0],
        "name": student[1],
        "status": student[2],
        "applied_department": student[3],
        "final_fee": float(student[4])
    }

    # Get detailed fee info from departments
    cur.execute("""
        SELECT tuition_fee, lab_fee, library_fee, transport_fee
        FROM departments
        WHERE dept_name = %s
    """, (student[3],))
    fee_info = cur.fetchone()

    if fee_info:
        response.update({
            "tuition_fee": float(fee_info[0]),
            "lab_fee": float(fee_info[1]),
            "library_fee": float(fee_info[2]),
            "transport_fee": float(fee_info[3])
        })

    # Get any applied scholarships
    cur.execute("""
        SELECT SUM(s.amount) as total_scholarship
        FROM scholarships_applied sa
        JOIN scholarships s ON sa.scholarship_id = s.scholarship_id
        WHERE sa.student_id = %s
    """, (student_id,))
    scholarship = cur.fetchone()

    if scholarship and scholarship[0]:
        response["scholarship"] = float(scholarship[0])

    return jsonify(response)






@app.route('/trackfee', methods=['GET'])
def track_fee():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({"error": "Student ID is required"}), 400

    cur = mysql.connection.cursor()

    # Get student's final fee from students_approved
    cur.execute("""
        SELECT final_fee 
        FROM students_approved 
        WHERE student_id = %s
    """, (student_id,))
    student = cur.fetchone()
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    total_fee = float(student[0])

    # Get all payments for this student
    cur.execute("""
        SELECT total_amount_paid, remaining_due_after_payment
        FROM fee_payments
        WHERE student_id = %s
        ORDER BY payment_date DESC
    """, (student_id,))
    payments = cur.fetchall()

    paid_amount = sum(float(payment[0]) for payment in payments) if payments else 0.0
    latest_balance = float(payments[0][1]) if payments else total_fee

    return jsonify({
        "student_id": student_id,
        "total_fee": total_fee,
        "paid_amount": paid_amount,
        "remaining_balance": latest_balance,
        "payment_history": [{
            "amount_paid": float(payment[0]),
            "remaining_balance": float(payment[1]),
            "payment_date": payment[2].strftime('%Y-%m-%d') if len(payment) > 2 else None
        } for payment in payments]
    })





if __name__ == '__main__':
    app.run(debug=True)
