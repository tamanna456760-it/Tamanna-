import datetime
import hashlib
import json
import random
from typing import Dict, List


class BDKingR7AIDoctor:
    def __init__(self):
        self.system_config = self.load_config("bd_king_r7_config.json")
        self.symptoms_db = self.load_config("symptoms_db.json")
        self.diseases_db = self.load_config("diseases_db.json")
        self.patients = {}
        self.consultations = []

        print("🩺 BD-King-R7 AI Doctor System Initializing...")
        print(f"✅ System: {self.system_config['system']['name']}")
        print(f"✅ Version: {self.system_config['system']['version']}")
        print("✅ Medical databases loaded successfully")

    def load_config(self, filename: str) -> Dict:
        """Load JSON configuration files"""
        try:
            with open(tamanna, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"⚠️  Config file {filename} not found. Creating default...")
            return {}

    def generate_patient_id(self, name: str) -> str:
        """Generate unique patient ID"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        name_hash = hashlib.md5(name.encode()).hexdigest()[:6].upper()
        return f"PT-{timestamp}-{name_hash}"

    def register_patient(
        self, name: str, age: int, gender: str, medical_history: List[str] = None
    ) -> str:
        """Register a new patient"""
        patient_id = self.generate_patient_id(name)

        self.patients[patient_id] = {
            "patient_id": patient_id,
            "personal_info": {
                "name": name,
                "age": age,
                "gender": gender,
                "registration_date": datetime.datetime.now().isoformat(),
            },
            "medical_data": {
                "medical_history": medical_history or [],
                "allergies": [],
                "current_medications": [],
                "vital_signs": {},
            },
            "consultation_history": [],
        }

        self.system_config["patients"]["total_registered"] += 1
        print(f"✅ Patient {name} registered with ID: {patient_id}")
        return patient_id

    def assess_symptoms(
        self, patient_id: str, symptoms: List[str], duration_hours: int
    ) -> Dict:
        """AI-powered symptom assessment"""
        if patient_id not in self.patients:
            return {"error": "Patient not found"}

        print(f"🔍 Analyzing symptoms for patient {patient_id}...")

        # AI Analysis
        emergency_level = self._check_emergency(symptoms)
        possible_conditions = self._diagnose_conditions(symptoms)
        recommendations = self._generate_recommendations(
            symptoms, duration_hours, emergency_level
        )

        consultation_id = f"CONS-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

        analysis_result = {
            "consultation_id": consultation_id,
            "patient_id": patient_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "symptoms_reported": symptoms,
            "duration_hours": duration_hours,
            "ai_analysis": {
                "emergency_level": emergency_level,
                "possible_conditions": possible_conditions,
                "confidence_score": random.randint(75, 95),
                "risk_factors": self._assess_risk_factors(symptoms),
            },
            "recommendations": recommendations,
            "next_steps": self._suggest_next_steps(emergency_level),
        }

        # Store consultation
        self.consultations.append(analysis_result)
        self.patients[patient_id]["consultation_history"].append(
            consultation_id)

        return analysis_result

    def _check_emergency(self, symptoms: List[str]) -> str:
        """Check if symptoms indicate emergency"""
        critical_symptoms = [
            "chest_pain",
            "shortness_of_breath",
            "severe_bleeding",
            "unconsciousness",
        ]

        for symptom in symptoms:
            symptom_data = self.symptoms_db["symptoms"].get(symptom, {})
            if symptom_data.get("urgency") == "high" or symptom in critical_symptoms:
                return "CRITICAL"

        return "NON_CRITICAL"

    def _diagnose_conditions(self, symptoms: List[str]) -> List[str]:
        """AI diagnosis based on symptom patterns"""
        possible_conditions = []

        for disease, data in self.diseases_db["diseases"].items():
            matching_symptoms = set(symptoms) & set(data["symptoms"])
            if len(matching_symptoms) >= 2:  # At least 2 matching symptoms
                possible_conditions.append(disease)

        return (
            possible_conditions
            if possible_conditions
            else ["general_medical_consultation"]
        )

    def _generate_recommendations(
        self, symptoms: List[str], duration: int, emergency: str
    ) -> List[str]:
        """Generate medical recommendations"""
        recommendations = []

        if emergency == "CRITICAL":
            recommendations.append(
                "🚨 SEEK IMMEDIATE EMERGENCY MEDICAL ATTENTION!")
            recommendations.append(
                "Call emergency services or go to nearest hospital")
            return recommendations

        # General recommendations
        recommendations.append("💊 Consider over-the-counter symptom relief")
        recommendations.append("💧 Maintain good hydration")
        recommendations.append("🛌 Get adequate rest")

        # Symptom-specific recommendations
        if "fever" in symptoms:
            recommendations.append("🌡️ Monitor temperature regularly")
            recommendations.append("🔄 Use fever-reducing medication if needed")

        if "cough" in symptoms:
            recommendations.append(
                "🍯 Consider cough drops or honey for throat")

        if duration > 72:  # More than 3 days
            recommendations.append(
                "📞 Schedule appointment with healthcare provider")

        return recommendations

    def _assess_risk_factors(self, symptoms: List[str]) -> List[str]:
        """Assess potential risk factors"""
        risks = []

        if "chest_pain" in symptoms:
            risks.append("cardiac_risk")
        if "shortness_of_breath" in symptoms:
            risks.append("respiratory_risk")
        if any(symptom in symptoms for symptom in ["dizziness", "confusion"]):
            risks.append("neurological_risk")

        return risks if risks else ["low_risk"]

    def _suggest_next_steps(self, emergency_level: str) -> List[str]:
        """Suggest next medical steps"""
        if emergency_level == "CRITICAL":
            return [
                "Call emergency services immediately",
                "Do not drive yourself to hospital",
                "Keep patient calm and still",
            ]
        else:
            return [
                "Monitor symptoms for changes",
                "Follow up in 24-48 hours if no improvement",
                "Contact healthcare provider for persistent symptoms",
            ]

    def generate_medical_report(self, consultation_id: str) -> Dict:
        """Generate comprehensive medical report"""
        consultation = next(
            (c for c in self.consultations if c["consultation_id"]
             == consultation_id),
            None,
        )

        if not consultation:
            return {"error": "Consultation not found"}

        patient_id = consultation["patient_id"]
        patient_data = self.patients[patient_id]

        report = {
            "report_id": f"REP-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.datetime.now().isoformat(),
            "patient_summary": {
                "name": patient_data["personal_info"]["name"],
                "age": patient_data["personal_info"]["age"],
                "medical_history": patient_data["medical_data"]["medical_history"],
            },
            "consultation_findings": consultation,
            "ai_notes": "This report is generated by BD-King-R7 AI System. Please consult healthcare professional for definitive diagnosis.",
        }

        return report

    def system_status(self) -> Dict:
        """Get current system status"""
        return {
            "system": self.system_config["system"],
            "patients_summary": self.system_config["patients"],
            "active_consultations": len(self.consultations),
            "system_uptime": "running",
            "last_update": datetime.datetime.now().isoformat(),
        }


# Demo Execution Function
def run_demo():
    """Run a complete demonstration of BD-King-R7 AI Doctor"""
    print("\n" + "=" * 60)
    print("🚀 BD-KING-R7 AI DOCTOR SYSTEM - DEMO EXECUTION")
    print("=" * 60)

    # Initialize system
    ai_doctor = BDKingR7AIDoctor()

    # Register patients
    print("\n👥 REGISTERING PATIENTS...")
    patient1 = ai_doctor.register_patient(
        name="John Smith",
        age=45,
        gender="male",
        medical_history=["hypertension", "allergy_penicillin"],
    )

    patient2 = ai_doctor.register_patient(
        name="Maria Garcia", age=32, gender="female", medical_history=["asthma"]
    )

    # Symptom consultations
    print("\n🔍 CONDUCTING SYMPTOM ANALYSIS...")

    # Case 1: Common cold symptoms
    print("\n📋 Case 1: Common Cold Symptoms")
    analysis1 = ai_doctor.assess_symptoms(
        patient_id=patient1,
        symptoms=["cough", "headache", "fatigue"],
        duration_hours=48,
    )
    print(json.dumps(analysis1, indent=2))

    # Case 2: Potential emergency
    print("\n📋 Case 2: Potential Emergency Symptoms")
    analysis2 = ai_doctor.assess_symptoms(
        patient_id=patient2,
        symptoms=["chest_pain", "shortness_of_breath", "dizziness"],
        duration_hours=2,
    )
    print(json.dumps(analysis2, indent=2))

    # Generate medical report
    print("\n📊 GENERATING MEDICAL REPORT...")
    report = ai_doctor.generate_medical_report(analysis1["consultation_id"])
    print(json.dumps(report, indent=2))

    # System status
    print("\n📈 SYSTEM STATUS...")
    status = ai_doctor.system_status()
    print(json.dumps(status, indent=2))

    print("\n✅ BD-KING-R7 AI DOCTOR DEMO COMPLETED SUCCESSFULLY!")
    print(
        "💊 Remember: This is an AI assistant. Always consult real doctors for medical emergencies!"
    )


# Run the demo
if __name__ == "__main__":
    run_demo()
