from flask import Blueprint, request, jsonify
from app.models import Patient, Course, Medicine
import json
import datetime

twilio_bp = Blueprint('twilio', __name__)

# Fetch the medicines for the patient that has times to take now.
@twilio_bp.route("/fetch-medicines", methods=["POST"])
def fetch_medicines():
    try:
        data = request.get_json()

        patient_phone = data.get("patient_phone")

        if not patient_phone:
            return jsonify({"error": "Missing required fields"}), 400

        patient = Patient.query.filter_by(phone=patient_phone).first()

        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        courses = Course.query.filter_by(patient_id=patient.id).all()

        if not courses:
            return jsonify({"error": "No courses found for this patient"}), 404

        medicines = []

        for course in courses:
            course_medicines = Medicine.query.filter_by(course_id=course.id).all()

            for medicine in course_medicines:
                times = json.loads(medicine.times)

                for time in times:
                    if time == datetime.now().strftime("%H:%M"):
                        medicines.append({
                            "name": medicine.name,
                            "time": time
                        })

        return jsonify(medicines), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500