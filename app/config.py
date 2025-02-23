from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv(override=True)

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,         # Number of connections to keep open
        "max_overflow": 5,       # Extra connections if pool is full
        "pool_recycle": 280,     # Refresh connections after 280 seconds
        "pool_pre_ping": True    # Test connection before using
    }
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
