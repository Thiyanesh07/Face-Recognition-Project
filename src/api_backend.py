from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS

DB_PATH = "attendance_system.db"

app = Flask(__name__)
CORS(app)  # Allow frontend (Streamlit, React, etc.) to call this API


# ---------- Helper ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Student Routes ----------
@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()
    roll_no = data.get("roll_no")
    name = data.get("name")

    if not roll_no or not name:
        return jsonify({"error": "roll_no and name are required"}), 400

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO students (roll_no, name) VALUES (?, ?)", (roll_no, name))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Student already exists"}), 409
    finally:
        conn.close()

    return jsonify({"message": "Student added successfully"}), 201


# ---------- Camera Routes ----------
@app.route("/cameras", methods=["GET"])
def get_cameras():
    conn = get_db_connection()
    cameras = conn.execute("SELECT * FROM cameras").fetchall()
    conn.close()
    return jsonify([dict(row) for row in cameras])


@app.route("/cameras", methods=["POST"])
def add_camera():
    data = request.get_json()
    ip_address = data.get("ip_address")

    if not ip_address:
        return jsonify({"error": "ip_address is required"}), 400

    conn = get_db_connection()
    conn.execute("INSERT INTO cameras (ip_address) VALUES (?)", (ip_address,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Camera added successfully"}), 201


# ---------- Attendance Routes ----------
@app.route("/attendance", methods=["GET"])
def get_attendance():
    """Fetch all attendance or filter by date/student."""
    date = request.args.get("date")
    roll_no = request.args.get("roll_no")

    conn = get_db_connection()
    query = "SELECT * FROM attendance"
    params = []

    if date or roll_no:
        query += " WHERE"
        conditions = []
        if date:
            conditions.append(" date=? ")
            params.append(date)
        if roll_no:
            conditions.append(" roll_no=? ")
            params.append(roll_no)
        query += " AND ".join(conditions)

    query += " ORDER BY detected_time DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/attendance", methods=["POST"])
def log_attendance():
    """Log attendance via API."""
    data = request.get_json()
    roll_no = data.get("roll_no")
    camera_id = data.get("camera_id")

    if not roll_no or not camera_id:
        return jsonify({"error": "roll_no and camera_id are required"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    detected_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Avoid duplicate entry same day
    c.execute("SELECT * FROM attendance WHERE roll_no=? AND date=? AND camera_id=?", (roll_no, date, camera_id))
    if c.fetchone():
        conn.close()
        return jsonify({"message": "Already marked present today"}), 200

    c.execute("INSERT INTO attendance (roll_no, camera_id, detected_time, date) VALUES (?, ?, ?, ?)",
              (roll_no, camera_id, detected_time, date))
    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance logged successfully"}), 201


# ---------- Root ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "Face Recognition Attendance API active 🚀"
    })


# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
