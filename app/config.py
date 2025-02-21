from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://u447378002_medifyteam:MedifyTeam2024@srv1554.hstgr.io/u447378002_medifydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Import and register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app