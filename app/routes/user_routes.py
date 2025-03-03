from flask import Blueprint, request, jsonify
from app.routes.auth_routes import token_required

user_bp = Blueprint('user', __name__)
@user_bp.route('/get-user', methods=['GET'])
@token_required
def get_db(current_user):
    try:
        user_data = {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
            "patients": []
        }

        for patient in current_user.patients:
            patient_data = {
                "id": patient.id,
                "name": patient.name,
                "age": patient.age,
                "phone": patient.phone,
                "created_at": patient.created_at.isoformat() if patient.created_at else None,
                "updated_at": patient.updated_at.isoformat() if patient.updated_at else None,
                "courses": []
            }

            for course in patient.courses:
                course_data = {
                    "id": course.id,
                    "name": course.name,
                    "created_at": course.created_at.isoformat() if course.created_at else None,
                    "updated_at": course.updated_at.isoformat() if course.updated_at else None,
                    "course_expiry": course.course_expiry.isoformat() if course.course_expiry else None,
                    "is_expired": course.isExpired,
                    "medicines": []
                }

                for medicine in course.medicines:
                    medicine_data = {
                        "id": medicine.id,
                        "name": medicine.name,
                        "duration": medicine.duration,
                        "times": medicine.get_times(),
                        "created_at": medicine.created_at.isoformat() if medicine.created_at else None,
                        "updated_at": medicine.updated_at.isoformat() if medicine.updated_at else None,
                        "expiry_at": medicine.expiry_at.isoformat() if medicine.expiry_at else None,
                        "is_expired": medicine.is_expired(),
                        "logs": []
                    }

                    for log in medicine.logs:
                        log_data = {
                            "id": log.id,
                            "is_taken": log.is_taken,
                            "created_at": log.created_at.isoformat() if log.created_at else None,
                            "updated_at": log.updated_at.isoformat() if log.updated_at else None,
                        }
                        medicine_data["logs"].append(log_data)

                    course_data["medicines"].append(medicine_data)
                
                patient_data["courses"].append(course_data)
            
            user_data["patients"].append(patient_data)
        
        return jsonify({"status": "success", "user": user_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
