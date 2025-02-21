from flask import Blueprint
from .auth_routes import auth_bp
from .patient_routes import patient_bp
from .user_routes import user_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(user_bp, url_prefix='/user')
