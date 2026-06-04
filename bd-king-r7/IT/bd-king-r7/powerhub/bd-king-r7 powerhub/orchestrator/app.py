# Simple orchestrator web app
import json
import os
from datetime import datetime

from flask import Flask, abort, jsonify, render_template_string, request
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.environ.get("DATABASE_URL", "sqlite:///reports.db")
API_TOKEN = os.environ.get("ORCHESTRATOR_TOKEN", "change-this-token")

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {
    },
)
Base = declarative_base()
Session = sessionmaker(bind=engine)
app = Flask(__name__)


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(128))
    timestamp = Column(DateTime)
    branch = Column(String(128))
    build_ok = Column(String(32))
    committed = Column(String(32))
    commit_sha = Column(String(64))
    payload = Column(Text)


Base.metadata.create_all(engine)


def require_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        abort(401)
    token = auth.split(" ", 1)[1].strip()
    if token != API_TOKEN:
        abort(403)


@app.route("/api/report", methods=["POST"])
def api_report():
    require_token()
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid json"}), 400
    session = Session()
    try:
        rep = Report(
            agent_id=data.get("agent_id"),
            timestamp=datetime.utcnow(),
            branch=data.get("branch", ""),
            build_ok=str(data.get("build_ok", False)),
            committed=str(data.get("committed", False)),
            commit_sha=data.get("commit_sha") or "",
            payload=json.dumps(data),
        )
        session.add(rep)
        session.commit()
        return jsonify({"status": "ok"}), 201
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/")
def index():
    session = Session()
    try:
        rows = session.query(Report).order_by(
            Report.id.desc()).limit(200).all()
    finally:
        session.close()
    # very small template for quick dashboard
    template = """
    <html><head><title>bd-king-r7 Orchestrator</title></head><body>
    <h1>bd-king-r7 Orchestrator - Recent Reports</h1>
    <table border=1 cellpadding=6>
    <tr><th>ID</th><th>Agent</th><th>Time</th><th>Branch</th><th>Build</th><th>Committed</th><th>Commit</th></tr>
    {% for r in rows %}
      <tr>
        <td>{{ r.id }}</td>
        <td>{{ r.agent_id }}</td>
        <td>{{ r.timestamp }}</td>
        <td>{{ r.branch }}</td>
        <td>{{ r.build_ok }}</td>
        <td>{{ r.committed }}</td>
        <td>{{ r.commit_sha }}</td>
      </tr>
    {% endfor %}
    </table>
    </body></html>
    """
    return render_template_string(template, rows=rows)
