import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Secret key from environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'PLACEHOLDER_SECRET_KEY')

DB_PATH = "attendance_system.db"

# ---------------- Database Initialization ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    roll_no TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )''')

    # Cameras table
    c.execute('''CREATE TABLE IF NOT EXISTS cameras (
                    camera_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL
                )''')

    # Attendance table
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT NOT NULL,
                    camera_id INTEGER NOT NULL,
                    detected_time TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (roll_no) REFERENCES students (roll_no),
                    FOREIGN KEY (camera_id) REFERENCES cameras (camera_id)
                )''')

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )''')

    # Preload users from environment variables (placeholders for GitHub)
    users = [
        (os.getenv("EMAIL1", "EMAIL1_PLACEHOLDER"), os.getenv("PWD1", "PWD1_PLACEHOLDER")),
        (os.getenv("EMAIL2", "EMAIL2_PLACEHOLDER"), os.getenv("PWD2", "PWD2_PLACEHOLDER")),
        (os.getenv("EMAIL3", "EMAIL3_PLACEHOLDER"), os.getenv("PWD3", "PWD3_PLACEHOLDER")),
        (os.getenv("EMAIL4", "EMAIL4_PLACEHOLDER"), os.getenv("PWD4", "PWD4_PLACEHOLDER"))
    ]

    for email, pwd in users:
        if email and pwd:
            c.execute("INSERT OR IGNORE INTO users (email, password_hash) VALUES (?, ?)",
                      (email, generate_password_hash(pwd)))

    conn.commit()
    conn.close()
    print("✅ Database initialized with authentication users (placeholders).")


# ---------------- JWT Token Protection ----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# ---------------- Authentication ----------------
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if not user or not check_password_hash(user[2], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': user[0],
        'email': user[1],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=4)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token})


# ---------------- Students ----------------
@app.route('/students', methods=['GET'])
@token_required
def get_students(current_user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = [{'roll_no': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(students)


@app.route('/students', methods=['POST'])
@token_required
def add_student(current_user):
    data = request.get_json()
    roll_no = data.get('roll_no')
    name = data.get('name')
    if not roll_no or not name:
        return jsonify({'error': 'Missing fields'}), 400
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO students (roll_no, name) VALUES (?, ?)", (roll_no, name))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Student {name} added successfully'})


# ---------------- Cameras ----------------
@app.route('/cameras', methods=['GET'])
@token_required
def get_cameras(current_user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM cameras")
    cameras = [{'camera_id': row[0], 'ip_address': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(cameras)


@app.route('/cameras', methods=['POST'])
@token_required
def add_camera(current_user):
    data = request.get_json()
    ip_address = data.get('ip_address')
    if not ip_address:
        return jsonify({'error': 'Missing IP address'}), 400
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO cameras (ip_address) VALUES (?)", (ip_address,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Camera {ip_address} added successfully'})


# ---------------- Attendance ----------------
@app.route('/attendance', methods=['GET'])
@token_required
def get_attendance(current_user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    rows = c.fetchall()
    conn.close()
    records = [{'attendance_id': r[0], 'roll_no': r[1], 'camera_id': r[2],
                'detected_time': r[3], 'date': r[4]} for r in rows]
    return jsonify(records)


@app.route('/attendance', methods=['POST'])
@token_required
def mark_attendance(current_user):
    data = request.get_json()
    roll_no = data.get('roll_no')
    camera_id = data.get('camera_id')
    if not roll_no or not camera_id:
        return jsonify({'error': 'Missing fields'}), 400

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    detected_time = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE roll_no=? AND date=? AND camera_id=?",
              (roll_no, date, camera_id))
    if c.fetchone():
        conn.close()
        return jsonify({'message': 'Attendance already marked for today'}), 200

    c.execute("INSERT INTO attendance (roll_no, camera_id, detected_time, date) VALUES (?, ?, ?, ?)",
              (roll_no, camera_id, detected_time, date))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Attendance logged for {roll_no} at {detected_time}'})


@app.route('/')
def home():
    return jsonify({'message': 'Secure Face Recognition Attendance API Running ✅'})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)