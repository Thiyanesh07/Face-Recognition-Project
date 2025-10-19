# Smart Attendance System

A comprehensive face recognition-based attendance management system built with FastAPI, FAISS vector database, and real-time WebSocket communication.

## 🚀 Features

- **Real-time Face Recognition**: Live camera feed with instant face detection and recognition
- **Student Registration**: Upload multiple photos per student for better recognition accuracy
- **WebSocket Communication**: Real-time attendance marking via WebSocket
- **Vector Database**: FAISS for fast and accurate face matching
- **Attendance Tracking**: Complete attendance records with timestamps
- **Modern Web Interface**: Responsive HTML/CSS/JavaScript frontend
- **Cooldown Protection**: Prevents duplicate attendance marking
- **Export Functionality**: Export attendance logs to CSV

## 🛠️ Technologies Used

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **MySQL**: Relational database for student and attendance data
- **FAISS**: Vector database for face embedding storage and search
- **DeepFace**: Face recognition library with FaceNet model
- **OpenCV**: Computer vision library for image processing
- **WebSockets**: Real-time communication between frontend and backend

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with responsive design
- **JavaScript (ES6+)**: Client-side functionality
- **WebRTC**: Camera access and video streaming

## 📁 Project Structure

```
Face-Recognition-Project/
├── backend/                    # FastAPI backend
│   ├── api/                   # API routes
│   │   ├── attendance_routes.py
│   │   └── student_routes.py
│   ├── core/                  # Configuration
│   │   └── config.py
│   ├── schemas/               # Pydantic models
│   │   ├── student.py
│   │   └── attendance.py
│   ├── services/              # Business logic
│   │   └── stream_manager.py
│   ├── main.py               # FastAPI application
│   └── requirements.txt      # Python dependencies
├── db/                       # Database files
│   ├── sql_db/              # MySQL database
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── crud.py          # Database operations
│   └── vector_db/           # FAISS vector database
│       ├── faiss_manager.py # FAISS operations
│       ├── face_index.bin   # Vector index (auto-generated)
│       └── index_to_id.json # Index mapping (auto-generated)
├── face_detection_and_recognition/
│   ├── models/              # ML model files
│   │   └── facenet_model.h5
│   ├── face_encoder.py      # Face embedding generation
│   ├── face_detector.py     # Face detection
│   ├── face_recognizer.py   # Main recognition logic
│   └── utils.py             # Utility functions
├── frontend/                # Web interface
│   ├── css/
│   │   └── style.css        # Styling
│   ├── js/
│   │   ├── main.js          # Main dashboard logic
│   │   └── register.js      # Registration logic
│   ├── assets/
│   │   └── logo.png         # Logo and icons
│   ├── index.html           # Main dashboard
│   └── register.html        # Student registration
├── dataset/                 # Student photos
│   └── raw_images/
│       ├── S001_John/       # Student folders
│       │   ├── front.jpg
│       │   ├── side.jpg
│       │   └── smiling.jpg
│       └── S002_Jane/
│           ├── 1.jpg
│           └── 2.jpg
├── scripts/                 # Utility scripts
│   ├── create_embeddings.py # Generate face embeddings
│   └── test_camera.py       # Test camera functionality
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Webcam/Camera
- Modern web browser with WebRTC support

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Face-Recognition-Project
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Setup MySQL database**
   ```sql
   CREATE DATABASE attendance_system;
   CREATE USER 'attendance_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON attendance_system.* TO 'attendance_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **Configure environment variables**
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=mysql+pymysql://attendance_user:your_password@localhost:3306/attendance_system
   VECTOR_DB_PATH=./db/vector_db
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```

6. **Open the frontend**
   Open `frontend/index.html` in your web browser

### First-Time Setup

1. **Register students**
   - Go to the registration page
   - Upload multiple clear photos of each student
   - The system will automatically generate face embeddings

2. **Test the system**
   ```bash
   python scripts/test_camera.py
   ```

3. **Start attendance tracking**
   - Open the main dashboard
   - Click "Start Camera" to enable webcam
   - Click "Start Recognition" to begin face recognition
   - Students will be automatically recognized and marked present

## 📖 Usage Guide

### Student Registration

1. Navigate to the registration page
2. Fill in student details:
   - **Student ID**: Unique identifier (e.g., S001, 2024001)
   - **Student Name**: Full name
   - **Email**: Optional email address
3. Upload multiple photos:
   - Include different angles (front, side, smiling)
   - Ensure good lighting and clear visibility
   - Avoid sunglasses, hats, or face coverings
4. Click "Register Student"
5. The system will process images and create face embeddings

### Attendance Tracking

1. Open the main dashboard
2. Click "Start Camera" to enable webcam access
3. Click "Start Recognition" to begin real-time recognition
4. Students will be automatically recognized when they appear in the camera
5. Attendance is marked with a 1-minute cooldown to prevent duplicates
6. View real-time attendance log on the dashboard

### Managing Attendance Records

- **View Records**: All attendance records are displayed in real-time
- **Export Data**: Click "Export Log" to download CSV file
- **Clear Log**: Click "Clear Log" to reset the current session
- **Statistics**: View daily attendance statistics

## 🔧 Configuration

### Database Configuration

Edit `backend/core/config.py` to modify database settings:

```python
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/database"
```

### Face Recognition Settings

Adjust recognition parameters in `backend/core/config.py`:

```python
FACE_DETECTION_CONFIDENCE = 0.7      # Face detection confidence threshold
FACE_RECOGNITION_THRESHOLD = 0.6     # Face recognition similarity threshold
EMBEDDING_DIMENSION = 512            # FaceNet embedding dimension
```

### WebSocket Settings

Modify WebSocket behavior in `frontend/main.js`:

```javascript
// Recognition interval (milliseconds)
setInterval(() => {
    this.captureAndSendFrame();
}, 2000);  // Send frame every 2 seconds
```

## 🧪 Testing

### Test Camera Functionality
```bash
python scripts/test_camera.py
```

### Test Face Recognition
```bash
python scripts/create_embeddings.py --test path/to/test/image.jpg
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get students
curl http://localhost:8000/api/students/

# Get attendance records
curl http://localhost:8000/api/attendance/records
```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not working**
   - Check browser permissions for camera access
   - Ensure camera is not being used by another application
   - Try refreshing the page

2. **Face recognition not working**
   - Ensure students are properly registered with clear photos
   - Check lighting conditions
   - Verify FAISS index is loaded (check backend logs)

3. **Database connection errors**
   - Verify MySQL is running
   - Check database credentials in `.env` file
   - Ensure database exists and user has proper permissions

4. **WebSocket connection failed**
   - Check if backend server is running
   - Verify WebSocket URL in frontend code
   - Check firewall settings

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your `.env` file:

```env
DEBUG=True
```

This will provide detailed logging information.

## 📊 Performance Optimization

### For Large Datasets

1. **Increase FAISS index size**:
   ```python
   # In faiss_manager.py
   self.index = faiss.IndexFlatL2(dimension)  # For small datasets
   # Use faiss.IndexIVFFlat for large datasets
   ```

2. **Optimize image processing**:
   - Resize images to standard dimensions
   - Use appropriate image quality settings
   - Consider batch processing for embeddings

3. **Database optimization**:
   - Add indexes for frequently queried columns
   - Use connection pooling
   - Consider read replicas for reporting

## 🔒 Security Considerations

1. **HTTPS in Production**: Use HTTPS for all communications
2. **Database Security**: Use strong passwords and restrict database access
3. **API Security**: Implement authentication and rate limiting
4. **Data Privacy**: Ensure compliance with privacy regulations
5. **Image Storage**: Consider encrypting stored images

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [DeepFace](https://github.com/serengil/deepface) for face recognition capabilities
- [FAISS](https://github.com/facebookresearch/faiss) for vector similarity search
- [OpenCV](https://opencv.org/) for computer vision tools

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `http://localhost:8000/docs`

---

**Note**: This system is designed for educational and small-scale use. For production environments, consider additional security measures, scalability improvements, and compliance requirements.