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
    app.json.sort_keys = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import register_blueprints
    register_blueprints(app)

    from app.scheduler.scheduler import start_scheduler
    start_scheduler(app)  # Pass the app instance

    return app
