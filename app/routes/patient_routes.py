from flask import Blueprint, request, jsonify
from app.config import db
from app.models import Patient, User
import uuid
from app.routes.auth_routes import token_required

patient_bp = Blueprint('patient', __name__)

# Create a new patient for a user
@patient_bp.route('/add-patient', methods=['POST'])
@token_required
def create_patient(curent_user):
    data = request.get_json()
    
    user_id = curent_user.id
    name = data.get('name')
    age = data.get('age')

    if not user_id or not name or not age:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Create new patient
    new_patient = Patient(
        id=str(uuid.uuid4()),
        name=name,
        age=age,
        user_id=user_id
    )
    
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'Patient created successfully', 'patient_id': new_patient.id}), 201

# Remove a patient
@patient_bp.route("/remove-patient/<string:patient_id>", methods=["DELETE"])
@token_required
def remove_patient(current_user, patient_id):

    if not patient_id:
        return jsonify({"error": "Missing patient_id"}), 400

    patient = Patient.query.get(patient_id)

    if not patient or patient.user_id != current_user.id:
        return jsonify({"error": "Patient not found or unauthorized"}), 404

    db.session.delete(patient)
    db.session.commit()

    return jsonify({"message": "Patient deleted successfully"}), 200

#Add medication to a patient
@patient_bp.route("/add-medication/<string:patient_id>", methods=["POST"])
@token_required
def add_medication(current_user, patient_id):
    data = request.get_json()

    medication_name = data.get("name")
    medication_dosage = data.get("dosage")

    if not medication_name or not medication_dosage:
        return jsonify({"error": "Missing required fields"}), 400

    patient = Patient.query.get(patient_id)

    if not patient or patient.user_id != current_user.id:
        return jsonify({"error": "Patient not found or unauthorized"}), 404

    patient.medication.append({"name": medication_name, "dosage": medication_dosage})
    db.session.commit()

    return jsonify({"message": "Medication added successfully"}), 201