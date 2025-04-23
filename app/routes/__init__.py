from flask import Blueprint
from .auth_routes import auth_bp
from .patient_routes import patient_bp
from .user_routes import user_bp
from app.scheduler.scheduler import twilio_bp

from .comment_routes import comments_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(twilio_bp, url_prefix='/twilio')
