from flask import Blueprint, request, jsonify
from app.models import User
from app.config import db
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import pytz

IST = pytz.timezone("Asia/Kolkata")

# Secret Key for JWT
SECRET_KEY = "your_secret_key"

auth_bp = Blueprint('auth', __name__)

# Verify auth by token 
def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        token = token.split("Bearer ")[1]  # Extract the actual token from the header
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# User Registration
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data or not all(key in data for key in ['name', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password before storing
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created', 'user_id': user.id}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e.__dict__['orig'])}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# USer Login
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not all(key in data for key in ['email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Invalid login credentials'}), 401

        # Generate JWT Token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.now(IST) + datetime.timedelta(hours=50)  # Token expires in 2 hours
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({'message': 'Logged in successfully', 'token': token, 'user_id': user.id}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
