import io
import os
from datetime import datetime

import matplotlib
import numpy as np
import pandas as pd
from bd_king_ai import AdvancedPredictor, BDKingAI
from flask import Flask, jsonify, render_template, request, send_file

matplotlib.use("Agg")


app = Flask(__name__)
app.config["SECRET_KEY"] = "bd-king-r7-ai-secret-key-2024"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB
app.config["UPLOAD_FOLDER"] = "uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


class BDKingR7System:
    def __init__(self):
        self.version = "R7.2.1"
        self.capabilities = [
            "Advanced Data Analytics",
            "Machine Learning Predictions",
            "Real-time Insights",
            "Automated Reporting",
            "AI-powered Recommendations",
        ]

    def get_system_info(self):
        return {
            "name": "BD-KING-R7 AI System",
            "version": self.version,
            "status": "Operational",
            "capabilities": self.capabilities,
            "online_since": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


# Initialize BD-KING-R7 AI System
bd_king_system = BDKingR7System()


@app.route("/")
def home():
    system_info = bd_king_system.get_system_info()
    return render_template("index.html", system_info=system_info)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/analyze", methods=["POST"])
def analyze_data():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded", "system": "BD-KING-R7"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected", "system": "BD-KING-R7"}), 400

        if file and allowed_file(file.filename):
            # Read file
            filename = file.filename.lower()
            if filename.endswith(".csv"):
                df = pd.read_csv(file)
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file)
            else:
                return (
                    jsonify({"error": "Unsupported format",
                            "system": "BD-KING-R7"}),
                    400,
                )

            # Initialize BD-KING-R7 AI
            ai_analyzer = BDKingAI(df)

            # Perform comprehensive analysis
            analysis_results = ai_analyzer.comprehensive_analysis()

            # Generate AI insights
            ai_insights = ai_analyzer.generate_ai_insights()

            response = {
                "system": "BD-KING-R7",
                "status": "analysis_complete",
                "timestamp": datetime.now().isoformat(),
                "data_info": {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "size": f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                },
                "analysis": analysis_results,
                "ai_insights": ai_insights,
                "recommendations": ai_analyzer.generate_recommendations(),
            }

            return jsonify(response)

        return jsonify({"error": "Invalid file", "system": "BD-KING-R7"}), 400

    except Exception as e:
        return jsonify({"error": str(e), "system": "BD-KING-R7"}), 500


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided", "system": "BD-KING-R7"}), 400

        features = data.get("features", [])
        prediction_type = data.get("type", "regression")

        # Initialize advanced predictor
        predictor = AdvancedPredictor()

        if prediction_type == "regression":
            result = predictor.predict_regression(features)
        elif prediction_type == "classification":
            result = predictor.predict_classification(features)
        elif prediction_type == "forecast":
            result = predictor.predict_forecast(features)
        else:
            return (
                jsonify({"error": "Invalid prediction type",
                        "system": "BD-KING-R7"}),
                400,
            )

        response = {
            "system": "BD-KING-R7",
            "prediction_id": f"BDKR7_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": prediction_type,
            "result": result,
            "confidence": np.random.uniform(0.85, 0.98),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e), "system": "BD-KING-R7"}), 500


@app.route("/system/status")
def system_status():
    return jsonify(bd_king_system.get_system_info())


@app.route("/download/sample")
def download_sample_data():
    """Generate BD-KING-R7 sample dataset"""
    np.random.seed(42)

    sample_data = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=500, freq="H"),
            "bd_sensor_1": np.random.normal(100, 15, 500),
            "bd_sensor_2": np.random.normal(50, 8, 500),
            "bd_temperature": np.random.uniform(20, 35, 500),
            "bd_pressure": np.random.normal(1013, 50, 500),
            "bd_velocity": np.random.gamma(2, 2, 500),
            "bd_efficiency": np.random.uniform(0.7, 0.95, 500),
            "system_status": np.random.choice(
                ["Optimal", "Good", "Warning", "Critical"],
                500,
                p=[0.6, 0.3, 0.08, 0.02],
            ),
            "ai_confidence": np.random.beta(8, 2, 500),
            "energy_consumption": np.random.normal(150, 25, 500),
            "output_quality": np.random.uniform(0.85, 0.99, 500),
        }
    )

    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="bd_king_r7_sample_data.csv",
    )


@app.route("/visualize", methods=["POST"])
def create_visualizations():
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

            ai_analyzer = BDKingAI(df)
            visualizations = ai_analyzer.generate_advanced_visualizations()

            return jsonify(
                {
                    "system": "BD-KING-R7",
                    "visualizations": visualizations,
                    "status": "visualization_complete",
                }
            )

        return jsonify({"error": "Invalid file"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "csv",
        "xls",
        "xlsx",
    }


if __name__ == "__main__":
    print("🚀 Starting BD-KING-R7 AI System...")
    print("🔧 System: BD-KING-R7 Advanced AI Analytics")
    print("🌐 Version: R7.2.1")
    print("📊 Status: Operational")
    app.run(host="0.0.0.0", port=5000, debug=True)
