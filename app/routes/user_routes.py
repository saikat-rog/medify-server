from flask import Blueprint, jsonify
from app.config import db
from app.models import User
from app.routes.auth_routes import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/patients', methods=['GET'])
@token_required
def get_user_patients(current_user):
    patients = [{'id': p.id, 'name': p.name, 'age': p.age} for p in current_user.patients]
    return jsonify({'user_id': current_user.id, 'patients': patients}), 200
