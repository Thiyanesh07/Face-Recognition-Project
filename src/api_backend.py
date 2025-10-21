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

# Use a strong secret key from .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

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

    # Preload users from environment variables
    users = [
        (os.getenv("EMAIL1"), os.getenv("PWD1")),
        (os.getenv("EMAIL2"), os.getenv("PWD2")),
        (os.getenv("EMAIL3"), os.getenv("PWD3")),
        (os.getenv("EMAIL4"), os.getenv("PWD4"))
    ]

    for email, pwd in users:
        if email and pwd:
            c.execute("INSERT OR IGNORE INTO users (email, password_hash) VALUES (?, ?)",
                      (email, generate_password_hash(pwd)))

    conn.commit()
    conn.close()
    print("✅ Database initialized with authentication users.")


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


# ---------------- Other APIs (Students, Cameras, Attendance) ----------------
# (Keep the same code as before, with @token_required on protected routes)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
