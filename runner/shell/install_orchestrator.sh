#!/usr/bin/env bash
# Quick installer for orchestrator (run on central server)
set -euo pipefail
REPO_DIR="/opt/bd-king-r7-orchestrator"
if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root or with sudo"
  exit 1
fi
echo "Creating ${REPO_DIR}"
mkdir -p "${REPO_DIR}"
chown "$SUDO_USER":"$SUDO_USER" "${REPO_DIR}" || true
cd "${REPO_DIR}"
cat > docker-compose.yml <<'EOF'
version: "3.8"
services:
  orchestrator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ORCHESTRATOR_TOKEN=${ORCHESTRATOR_TOKEN:-change-this-token}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///reports.db}
    volumes:
      - ./data:/app
EOF
cat > Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV FLASK_APP=app.py
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app", "--workers", "3"]
EOF
cat > requirements.txt <<'EOF'
Flask==2.2.5
SQLAlchemy==1.4.57
gunicorn==20.1.0
requests==2.31.0
python-dotenv==1.0.0
EOF
cat > app.py <<'EOF'
# (the app.py contents from orchestrator/app.py should be pasted here)
EOF
mkdir -p data
chown -R "$SUDO_USER":"$SUDO_USER" data
echo "Orchestrator skeleton created at ${REPO_DIR}."
echo "Edit app.py, set ORCHESTRATOR_TOKEN and DATABASE_URL in environment or .env, then run:"
echo "  cd ${REPO_DIR} && docker-compose up -d --build"