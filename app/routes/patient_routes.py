from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from app.config import db
from app.models import Patient, User, Course, Medicine
import json
from app.routes.auth_routes import token_required

patient_bp = Blueprint('patient', __name__)


# PATIENT
# Create a new patient for a user
@patient_bp.route('/add-patient', methods=['POST'])
@token_required
def create_patient(current_user):
    try:
        data = request.get_json()

        user_id = current_user.id
        name = data.get('name')
        age = data.get('age')
        phone = data.get('phone')

        if not user_id or not name or not age or not phone:
            return jsonify({'error': 'Missing required fields'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        new_patient = Patient(
            name=name,
            age=age,
            phone=phone,
            user_id=user_id
        )

        db.session.add(new_patient)
        db.session.commit()

        return jsonify({'message': 'Patient created successfully', 'patient_id': new_patient.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Remove a patient from a user
@patient_bp.route("/remove-patient/<string:patient_id>", methods=["DELETE"])
@token_required
def remove_patient(current_user, patient_id):
    try:
        if not patient_id:
            return jsonify({"error": "Missing patient_id"}), 400

        patient = Patient.query.get(patient_id)

        if not patient or patient.user_id != current_user.id:
            return jsonify({"error": "Patient not found or unauthorized"}), 404

        db.session.delete(patient)
        db.session.commit()

        return jsonify({"message": "Patient deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# COURSE
# Add a course to a patient [Course name, Medicine names, Duration, Times are required fields]
@patient_bp.route("/add-course/<string:patient_id>", methods=["POST"])
@token_required
def add_course(current_user, patient_id):
    try:
        data = request.get_json()

        course_name = data.get("course_name")
        medicine_name = data.get("medicine_name")
        medicine_duration = data.get("medicine_duration")
        medicine_times = data.get("medicine_times")

        if not medicine_name or not medicine_times:
            return jsonify({"error": "Missing required fields"}), 400

        patient = Patient.query.get(patient_id)

        if not patient or patient.user_id != current_user.id:
            return jsonify({"error": "Patient not found or unauthorized"}), 404

        new_course = Course(
            name=course_name,
            patient_id=patient_id
        )

        db.session.add(new_course)
        db.session.flush()  # Ensure new_course.id is generated before using it

        new_medicine = Medicine(
            course_id=new_course.id,
            name=medicine_name,
            duration=medicine_duration,
            times=json.dumps(medicine_times)
        )

        db.session.add(new_medicine)
        db.session.commit()

        return jsonify({"message": "Course with medication added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Delete a course from a patient
@patient_bp.route("/delete-course/<string:course_id>", methods=["DELETE"])
@token_required
def delete_course(current_user, course_id):
    try:
        # Find the course by ID
        course = Course.query.filter_by(id=course_id).first()
        
        if not course or course.patient.user_id != current_user.id:
            return jsonify({"error": "Course not found or unauthorized"}), 404

        # Delete the course
        db.session.delete(course)
        db.session.commit()

        return jsonify({"message": "Course deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Get all the courses for a patient
@patient_bp.route("/get-all-courses/<string:patient_id>", methods=["GET"])
@token_required
def get_courses(current_user, patient_id):
    try:
        patient = Patient.query.get(patient_id)

        if not patient or patient.user_id != current_user.id:
            return jsonify({"error": "Patient not found or unauthorized"}), 404

        courses = Course.query.filter_by(patient_id=patient_id).all()

        if not courses:
            return jsonify({"message": "No courses found"}), 200

        response = []
        for course in courses:
            response.append({
                "id": course.id,
                "name": course.name
            })

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
# MEDICINE
# Add medicine and times to a an existing course
@patient_bp.route("/add-medicine/<string:course_id>", methods=["POST"])
@token_required
def add_medicine(current_user, course_id):
    try:
        data = request.get_json()

        medicine_name = data.get("medicine_name")
        medicine_times = data.get("medicine_times")
        medicine_duration = data.get("medicine_duration")

        if not medicine_name or not medicine_times:
            return jsonify({"error": "Missing required fields"}), 400

        course = Course.query.get(course_id)

        if not course or course.patient.user_id != current_user.id:
            return jsonify({"error": "Course not found or unauthorized"}), 404

        new_medicine = Medicine(
            course_id=course_id,
            name=medicine_name,
            duration=medicine_duration,
            times=json.dumps(medicine_times)
        )

        db.session.add(new_medicine)
        db.session.commit()

        return jsonify({"message": "Medicine added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# Get all medicine in the course with the times
@patient_bp.route("/get-medicines/<string:course_id>", methods=["GET"])
@token_required
def get_medicines(current_user, course_id):
    try:
        course = Course.query.get(course_id)

        if not course or course.patient.user_id != current_user.id:
            return jsonify({"error": "Course not found or unauthorized"}), 404

        medicines = Medicine.query.filter_by(course_id=course_id).all()

        if not medicines:
            return jsonify({"message": "No medicines found"}), 200

        response = []
        for medicine in medicines:
            response.append({
                "id": medicine.id,
                "name": medicine.name,
                "times": json.loads(medicine.times)
            })

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    
# Delete medicine in the course
@patient_bp.route("/delete-medicine/<string:medicine_id>", methods=["DELETE"])
@token_required
def delete_medicine(current_user, medicine_id):
    try:
        if not medicine_id:
            return jsonify({"error": "Missing medicine_id"}), 400

        medicine = Medicine.query.get(medicine_id)

        if not medicine or medicine.course.patient.user_id != current_user.id:
            return jsonify({"error": "Medicine not found or unauthorized"}), 404

        db.session.delete(medicine)
        db.session.commit()

        return jsonify({"message": "Medicine deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
