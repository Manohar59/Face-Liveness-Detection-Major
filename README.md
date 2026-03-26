🔐 Face Liveness Detection Based Authentication & Attendance System
📌 Overview

This project is a real-time face recognition system with liveness detection designed to provide secure authentication and automated attendance management. It prevents spoofing attacks using techniques like blink detection and facial movement analysis.

🚀 Features
👤 User Enrollment with Face Capture
🔍 Real-Time Face Detection
👁️ Liveness Detection (Blink + Movement)
🔐 Face Recognition using Embeddings
📝 Automatic Attendance Recording
📊 Attendance Dashboard
📁 Export Attendance to Excel
⚠️ Anti-Spoof Detection (Screen/Photo Detection)
🔄 Reset System Option

🛠️ Tech Stack
Frontend: Streamlit
Backend: Python
Computer Vision: OpenCV, Dlib
Database: SQLite
Data Handling: NumPy, Pandas

📂 Project Structure
.
├── streamlit_app.py
├── database/
├── captured_faces/
├── models/
│   ├── shape_predictor_68_face_landmarks.dat
│   └── dlib_face_recognition_resnet_model_v1.dat
├── attendance.csv
├── requirements.txt

⚙️ Installation
1. Clone Repository
git clone https://github.com/https:/github.com/Manohar59/https://github.com/Manohar59/Face-Liveness-Detection-Major.git


2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

▶️ Run the Application
streamlit run streamlit_app.py

📊 How It Works
Enroll User – Capture face and store embeddings
Authenticate – Perform liveness detection
Recognition – Match face with stored data
Attendance – Automatically mark attendance
Dashboard – View and export records

🎯 Use Cases
🎓 College Attendance Systems
🏢 Office Employee Monitoring
🔐 Secure Access Control
🧠 Biometric Authentication Systems

⚠️ Limitations
Performance may vary in low lighting
Requires webcam access
Accuracy depends on face visibility

🔮 Future Enhancements
🤖 Deep learning-based models
☁️ Cloud database integration
📱 Mobile app support
👥 Multi-face detection
🧬 Advanced anti-spoofing

🤝 Contributing
Contributions are welcome! Fork the repo and submit a pull request.

📜 License

This project is licensed under the MIT License.

⭐ Acknowledgements
OpenCV
Dlib
Streamlit


