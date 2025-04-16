from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

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
    CORS(app)
    app.config.from_object(Config)
    app.json.sort_keys = False

    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate.init_app(app, db)

    from app.routes import register_blueprints
    register_blueprints(app)

    if not os.environ.get("FLASK_CLI"):
        from app.scheduler.scheduler import start_scheduler
        from app.scheduler.scheduler import scheduler

        if not scheduler.running:
            start_scheduler(app)

    return app
