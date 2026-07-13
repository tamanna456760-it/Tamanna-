Face Detector AI

A Python-based Face Detection application built using OpenCV, MediaPipe, and Flask. The project detects human faces from images, webcams, and video streams for educational and authorized use.

Features

- Face Detection from Images
- Real-time Webcam Face Detection
- Video File Face Detection
- MediaPipe Face Detection
- OpenCV Haar Cascade Detection
- Flask Web Interface
- Docker Support
- GitHub Actions CI/CD
- Cross-platform (Windows, Linux, macOS)

Project Structure

face-detector/
├── app.py
├── detector/
├── models/
├── static/
├── templates/
├── config/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .github/workflows/face-detector.yml

Installation

git clone https://github.com/USERNAME/face-detector.git

cd face-detector

pip install -r requirements.txt

Run

python app.py

Open your browser:

http://127.0.0.1:5000

Requirements

- Python 3.12+
- OpenCV
- MediaPipe
- NumPy
- Flask
- Pillow

Docker

docker-compose up --build

GitHub Actions

Continuous Integration automatically:

- Install dependencies
- Run tests
- Verify project builds

Workflow file:

.github/workflows/face-detector.yml

Security & Privacy

This software is intended only for authorized and lawful use. Users are responsible for complying with applicable laws, platform terms of service, and privacy requirements. Do not use it to collect or analyze people's images without appropriate permission.

License

MIT License

Author

Tamanna AI