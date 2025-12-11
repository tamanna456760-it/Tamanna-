import io
import json
import os
import secrets
from datetime import datetime

import matplotlib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, session
from google_sync import GoogleSyncManager
from master_doctor_ai import MasterDoctorAI, MedicalAnalyzer

matplotlib.use("Agg")


app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["GOOGLE_CREDENTIALS"] = "credentials/google_credentials.json"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


class MasterDoctorSystem:
    def __init__(self):
        self.system_name = "Master Doctor AI"
        self.version = "MD-2.0.1"
        self.google_sync = GoogleSyncManager(app.config["GOOGLE_CREDENTIALS"])

    def get_system_status(self):
        return {
            "system": self.system_name,
            "version": self.version,
            "status": "Operational",
            "google_sync": self.google_sync.get_sync_status(),
            "last_updated": datetime.now().isoformat(),
            "features": [
                "Medical Data Analysis",
                "Patient Diagnostics",
                "Treatment Recommendations",
                "Google Drive Sync",
                "Real-time Monitoring",
                "AI-powered Insights",
            ],
        }


# Initialize Master Doctor AI System
master_doctor = MasterDoctorSystem()


@app.route("/")
def home():
    system_status = master_doctor.get_system_status()
    return render_template("index.html", system_status=system_status)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/sync")
def sync_interface():
    return render_template("sync.html")


@app.route("/analyze")
def analyze_interface():
    return render_template("analysis.html")


# Google Sync Endpoints
@app.route("/api/google/auth")
def google_auth():
    """Initialize Google OAuth flow"""
    try:
        auth_url = master_doctor.google_sync.get_authorization_url()
        return jsonify({"auth_url": auth_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get("code")
        if code:
            credentials = master_doctor.google_sync.exchange_code(code)
            session["google_credentials"] = credentials.to_json()
            return jsonify(
                {"status": "success", "message": "Google authentication successful"}
            )
        return jsonify({"error": "No authorization code"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/google/sync/upload", methods=["POST"])
def google_upload():
    """Upload analysis results to Google Drive"""
    try:
        if "google_credentials" not in session:
            return jsonify({"error": "Not authenticated with Google"}), 401

        data = request.get_json()
        filename = data.get(
            "filename",
            f"master_doctor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        content = data.get("content", {})

        result = master_doctor.google_sync.upload_to_drive(
            session["google_credentials"], filename, json.dumps(
                content, indent=2)
        )

        return jsonify({"status": "success", "file_id": result["id"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/google/sync/download", methods=["POST"])
def google_download():
    """Download data from Google Drive"""
    try:
        if "google_credentials" not in session:
            return jsonify({"error": "Not authenticated with Google"}), 401

        data = request.get_json()
        file_id = data.get("file_id")

        if file_id:
            content = master_doctor.google_sync.download_from_drive(
                session["google_credentials"], file_id
            )
            return jsonify({"status": "success", "content": content})
        else:
            # List available files
            files = master_doctor.google_sync.list_drive_files(
                session["google_credentials"]
            )
            return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/google/sync/sheets", methods=["POST"])
def google_sheets_sync():
    """Sync data with Google Sheets"""
    try:
        if "google_credentials" not in session:
            return jsonify({"error": "Not authenticated with Google"}), 401

        data = request.get_json()
        spreadsheet_id = data.get("spreadsheet_id")
        sheet_data = data.get("data", [])
        range_name = data.get("range", "Sheet1!A1")

        if spreadsheet_id and sheet_data:
            result = master_doctor.google_sync.update_google_sheet(
                session["google_credentials"], spreadsheet_id, range_name, sheet_data
            )
            return jsonify(
                {"status": "success",
                    "updated_cells": result.get("updatedCells")}
            )
        else:
            return jsonify({"error": "Missing spreadsheet_id or data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Medical Analysis Endpoints
@app.route("/api/analyze/medical", methods=["POST"])
def analyze_medical_data():
    """Analyze medical data"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if file and allowed_file(file.filename):
            # Read medical data
            if file.filename.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file)
            else:
                return jsonify({"error": "Unsupported file format"}), 400

            # Initialize Master Doctor AI
            medical_ai = MasterDoctorAI(df)

            # Perform comprehensive medical analysis
            analysis_results = medical_ai.comprehensive_medical_analysis()

            # Generate medical insights
            medical_insights = medical_ai.generate_medical_insights()

            response = {
                "system": "Master Doctor AI",
                "status": "analysis_complete",
                "timestamp": datetime.now().isoformat(),
                "patient_count": len(df),
                "analysis": analysis_results,
                "insights": medical_insights,
                "recommendations": medical_ai.generate_treatment_recommendations(),
                "risk_assessment": medical_ai.assess_patient_risks(),
            }

            return jsonify(response)

        return jsonify({"error": "Invalid file type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/symptoms", methods=["POST"])
def analyze_symptoms():
    """Analyze patient symptoms"""
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", [])
        patient_data = data.get("patient_data", {})

        analyzer = MedicalAnalyzer()
        diagnosis = analyzer.analyze_symptoms(symptoms, patient_data)

        return jsonify(
            {
                "system": "Master Doctor AI",
                "diagnosis": diagnosis,
                "confidence": diagnosis.get("confidence", 0),
                "recommended_tests": diagnosis.get("recommended_tests", []),
                "urgency": diagnosis.get("urgency", "low"),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/lab_results", methods=["POST"])
def analyze_lab_results():
    """Analyze laboratory results"""
    try:
        data = request.get_json()
        lab_results = data.get("lab_results", {})
        patient_info = data.get("patient_info", {})

        analyzer = MedicalAnalyzer()
        analysis = analyzer.analyze_lab_results(lab_results, patient_info)

        return jsonify(
            {
                "system": "Master Doctor AI",
                "lab_analysis": analysis,
                "abnormal_values": analysis.get("abnormal_values", []),
                "interpretation": analysis.get("interpretation", {}),
                "follow_up": analysis.get("follow_up_recommendations", []),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict/disease", methods=["POST"])
def predict_disease_risk():
    """Predict disease risk based on patient data"""
    try:
        data = request.get_json()
        patient_data = data.get("patient_data", {})

        medical_ai = MasterDoctorAI()
        prediction = medical_ai.predict_disease_risk(patient_data)

        return jsonify(
            {
                "system": "Master Doctor AI",
                "prediction_id": f"MD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "risk_assessment": prediction,
                "prevention_recommendations": prediction.get(
                    "prevention_recommendations", []
                ),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/visualize/medical", methods=["POST"])
def create_medical_visualizations():
    """Create medical data visualizations"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file and allowed_file(file.filename):
            df = (
                pd.read_csv(file)
                if file.filename.endswith(".csv")
                else pd.read_excel(file)
            )

            medical_ai = MasterDoctorAI(df)
            visualizations = medical_ai.generate_medical_visualizations()

            return jsonify(
                {
                    "system": "Master Doctor AI",
                    "visualizations": visualizations,
                    "status": "visualization_complete",
                }
            )

        return jsonify({"error": "Invalid file"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/system/status")
def system_status():
    """Get system status"""
    return jsonify(master_doctor.get_system_status())


@app.route("/api/download/medical_sample")
def download_medical_sample():
    """Download sample medical data"""
    np.random.seed(42)

    sample_data = pd.DataFrame(
        {
            "patient_id": range(1, 101),
            "age": np.random.randint(18, 80, 100),
            "gender": np.random.choice(["Male", "Female"], 100),
            "blood_pressure_systolic": np.random.normal(120, 15, 100),
            "blood_pressure_diastolic": np.random.normal(80, 10, 100),
            "heart_rate": np.random.normal(72, 10, 100),
            "cholesterol": np.random.normal(200, 40, 100),
            "blood_sugar": np.random.normal(100, 20, 100),
            "bmi": np.random.normal(25, 5, 100),
            "smoker": np.random.choice([0, 1], 100, p=[0.7, 0.3]),
            "diabetic": np.random.choice([0, 1], 100, p=[0.8, 0.2]),
            "symptoms": np.random.choice(
                ["None", "Headache", "Chest Pain", "Fatigue", "Dizziness"], 100
            ),
            "diagnosis": np.random.choice(
                ["Healthy", "Hypertension", "Diabetes",
                    "Hyperlipidemia", "Unknown"],
                100,
            ),
        }
    )

    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="master_doctor_sample_data.csv",
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "csv",
        "xls",
        "xlsx",
    }


if __name__ == "__main__":
    print("🏥 Starting Master Doctor AI System...")
    print("🔬 System: Master Doctor AI Medical Analytics")
    print("🌐 Version: MD-2.0.1")
    print("📊 Status: Operational")
    print("🔄 Google Sync: Ready")
    app.run(host="0.0.0.0", port=5000, debug=True)
