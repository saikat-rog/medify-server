from app.config import db
import uuid
import datetime

# Function to generate unique UUIDs
def generate_uuid():
    return str(uuid.uuid4())

# User model (Account holder)
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    # Relationship: One user has multiple patients
    patients = db.relationship("Patient", backref="user", cascade="all, delete-orphan")

# Patient model (Grandparent/Parent)
class Patient(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

# Medicine model
class Medicine(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Medicine schedule (Time + Duration)
class Schedule(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patient.id'), nullable=False)
    medicine_id = db.Column(db.String(36), db.ForeignKey('medicine.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    days_remaining = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    # Relationship (Optional, only needed if frequently accessing patients/medicines)
    patient = db.relationship("Patient", backref="schedules", lazy=True)
    medicine = db.relationship("Medicine", backref="schedules", lazy=True)

# Medicine Consumption Log
class ConsumptionLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    schedule_id = db.Column(db.String(36), db.ForeignKey('schedule.id'), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)  # Whether the patient confirmed intake
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    schedule = db.relationship("Schedule", backref="logs", lazy=True)
