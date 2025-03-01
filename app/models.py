from app.config import db
import uuid
from datetime import datetime, timezone, timedelta
import json
from sqlalchemy.sql import func
import pytz
from sqlalchemy import DateTime

IST = pytz.timezone("Asia/Kolkata")


# Function to generate unique UUIDs
def generate_uuid():
    return str(uuid.uuid4())

# User model (Account holder)
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(DateTime(timezone=True), default=datetime.now(IST))
    updated_at = db.Column(DateTime(timezone=True), onupdate=datetime.now(IST))

    # Relationship: One user has multiple patients
    patients = db.relationship("Patient", backref="user", cascade="all, delete-orphan")

# Patient model (Grandparent/Parent)
class Patient(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(100), nullable=True)
    created_at = db.Column(DateTime(timezone=True), default=datetime.now(IST))
    updated_at = db.Column(DateTime(timezone=True), onupdate=datetime.now(IST))

    # Relationship: A patient has multiple courses
    courses = db.relationship("Course", backref="patient", cascade="all, delete-orphan")

# Course model
class Course(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    patient_id = db.Column(db.String(36), db.ForeignKey('patient.id'), nullable=False)
    created_at = db.Column(DateTime(timezone=True), default=datetime.now(IST))
    updated_at = db.Column(DateTime(timezone=True), onupdate=datetime.now(IST))

    # Relationship with medicines
    medicines = db.relationship("Medicine", backref="course", cascade="all, delete-orphan")
    
    @property
    def course_expiry(self):
        """Returns the latest expiry date among all medicines in the course."""
        latest_medicine = max(self.medicines, key=lambda med: med.expiry_at, default=None)
        return latest_medicine.expiry_at if latest_medicine else None
    
    @property
    def isExpired(self):
        """Check if the course has expired based on the latest medicine expiry date."""
        return self.course_expiry and self.course_expiry < datetime.now(timezone.IST)

# Medicine model
class Medicine(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id'), nullable=False)  # Fixed FK
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in days
    times = db.Column(db.String(500), nullable=False)  # Store multiple times as JSON string
    created_at = db.Column(DateTime(timezone=True), default=datetime.now(IST))
    updated_at = db.Column(DateTime(timezone=True), onupdate=datetime.now(IST))
    expiry_at = db.Column(DateTime(timezone=True))  # Calculated based on duration

    logs = db.relationship("MedicineLog", backref="medicine", cascade="all, delete-orphan")

        
    def set_times(self, times_list):
        """Store list of times as a JSON string"""
        self.times = json.dumps(times_list)

    def get_times(self):
        """Retrieve list of times as a Python list"""
        return json.loads(self.times) if self.times else []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = self.created_at or datetime.now(IST)
        self.expiry_at = self.created_at + timedelta(days=self.duration)
        
    def is_expired(self):
        """Check if the medicine has expired"""
        return datetime.now(IST) > self.expiry_at.astimezone(IST) if self.expiry_at.astimezone(IST) else False
    
# Medicine log model
class MedicineLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    medicine_id = db.Column(db.String(36), db.ForeignKey('medicine.id'), nullable=False)
    is_taken = db.Column(db.Boolean, default=False)  # True if medicine was taken
    created_at = db.Column(DateTime(timezone=True), default=datetime.now(IST))
    updated_at = db.Column(DateTime(timezone=True), onupdate=datetime.now(IST))