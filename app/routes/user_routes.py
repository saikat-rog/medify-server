from flask import Blueprint, jsonify
from app.config import db
from app.models import User
from app.routes.auth_routes import token_required

user_bp = Blueprint('user', __name__)

# Get complete user data
@user_bp.route('/get-user', methods=['GET'])
@token_required
def get_db(current_user):
    try:
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'patients': []
        }

        for patient in user.patients:
            patient_data = {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'phone': patient.phone,
                'created_at': patient.created_at,
                'updated_at': patient.updated_at,
                'courses': []
            }

            for course in patient.courses:
                course_data = {
                    'id': course.id,
                    'name': course.name,
                    'created_at': course.created_at,
                    'updated_at': course.updated_at,
                    'medicines': []
                }

                for medicine in course.medicines:
                    medicine_data = {
                        'id': medicine.id,
                        'name': medicine.name,
                        'duration': medicine.duration,
                        'times': medicine.get_times(),
                        'created_at': medicine.created_at,
                        'updated_at': medicine.updated_at,
                        'logs': []
                    }

                    for log in medicine.logs:
                        log_data = {
                            'id': log.id,
                            'date': log.date.strftime('%Y-%m-%d'),
                            'time_taken': log.time_taken.strftime('%H:%M:%S'),
                            'is_taken': log.is_taken
                        }
                        medicine_data['logs'].append(log_data)

                    course_data['medicines'].append(medicine_data)

                patient_data['courses'].append(course_data)

            user_data['patients'].append(patient_data)

        return jsonify(user_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
