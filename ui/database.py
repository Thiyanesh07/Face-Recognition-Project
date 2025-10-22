import sqlite3
from datetime import datetime

DB_PATH = "attendance_system.db"

def init_db():
    """Initialize the database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- Create Tables ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            roll_no TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            camera_id INTEGER NOT NULL,
            detected_time TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (roll_no) REFERENCES students (roll_no),
            FOREIGN KEY (camera_id) REFERENCES cameras (camera_id)
        )
    ''')

    # --- Preload Student Data (updated order) ---
    students_data = [
        ("7376241CS146", "Boomika S"),
        ("7376241CS405", "Sri Midhuna S K"),
        ("7376242AD328", "Thiyanesh D"),
        ("7376242IT333", "Varshini S"),
        ("7376241CS472", "Varun S"),
        ("7376241CS465", "Vihashini S V"),
        ("7376241CS476", "Yuvashri M")
    ]

    for roll_no, name in students_data:
        c.execute("INSERT OR IGNORE INTO students (roll_no, name) VALUES (?, ?)", (roll_no, name))

    conn.commit()
    conn.close()
    print("✅ Database initialized and student data inserted successfully (updated order).")


def add_camera(ip_address):
    """Register a new camera."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO cameras (ip_address) VALUES (?)", (ip_address,))
    conn.commit()
    conn.close()
    print(f"📸 Camera added: {ip_address}")


def log_attendance(roll_no, camera_id):
    """Log student's attendance if not already marked for today."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    detected_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Avoid duplicate entries in the same day
    c.execute('''
        SELECT * FROM attendance 
        WHERE roll_no=? AND date=? AND camera_id=?
    ''', (roll_no, date, camera_id))
    
    if c.fetchone():
        conn.close()
        print(f"⚠️ Attendance already marked today for {roll_no}")
        return

    c.execute('''
        INSERT INTO attendance (roll_no, camera_id, detected_time, date)
        VALUES (?, ?, ?, ?)
    ''', (roll_no, camera_id, detected_time, date))

    conn.commit()
    conn.close()
    print(f"✅ Attendance logged: {roll_no} from Camera {camera_id} at {detected_time}")


# --- Run directly to initialize DB ---
if __name__ == "__main__":
    init_db()