from app.config import db
import uuid
from datetime import datetime, timedelta
import json
from sqlalchemy.sql import func
from sqlalchemy import DateTime


# Function to generate unique UUIDs
def generate_uuid():
    return str(uuid.uuid4())

# User model (Account holder)
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(DateTime(), default=func.now())
    updated_at = db.Column(DateTime(), onupdate=func.now())

    # Relationship: One user has multiple patients
    patients = db.relationship("Patient", backref="user", cascade="all, delete-orphan")

# Patient model (Grandparent/Parent)
class Patient(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(100), nullable=True)
    created_at = db.Column(DateTime(), default=func.now())
    updated_at = db.Column(DateTime(), onupdate=func.now())

    # Relationship: A patient has multiple courses
    courses = db.relationship("Course", backref="patient", cascade="all, delete-orphan")

# Course model
class Course(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    patient_id = db.Column(db.String(36), db.ForeignKey('patient.id'), nullable=False)
    created_at = db.Column(DateTime(), default=func.now())
    updated_at = db.Column(DateTime(), onupdate=func.now())

    # Relationship with medicines
    medicines = db.relationship("Medicine", backref="course", cascade="all, delete-orphan")
    
    @property
    def course_expiry(self):
        """Returns the latest expiry date among all medicines in the course."""
        latest_medicine = max(self.medicines, key=lambda med: med.expiry_at, default=None)
        return latest_medicine.expiry_at if latest_medicine else None
    
    @property
    def is_expired(self):
        """Check if the course has expired based on the latest medicine expiry date."""
        return self.course_expiry and self.course_expiry < datetime.utcnow()

# Medicine model
class Medicine(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id'), nullable=False)  # Fixed FK
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in days
    times = db.Column(db.String(500), nullable=False)  # Store multiple times as JSON string
    created_at = db.Column(DateTime(), default=func.now())
    updated_at = db.Column(DateTime(), onupdate=func.now())
    expiry_at = db.Column(DateTime(), nullable=False)  # Calculated based on duration

    logs = db.relationship("MedicineLog", backref="medicine", cascade="all, delete-orphan")

        
    def set_times(self, times_list):
        """Store list of times as a JSON string"""
        self.times = json.dumps(times_list)

    def get_times(self):
        """Retrieve list of times as a Python list"""
        return json.loads(self.times) if self.times else []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure duration is set before using it
        if self.duration is not None:
            self.expiry_at = datetime.utcnow() + timedelta(days=self.duration)
        else:
            self.expiry_at = None  # Handle case where duration is missing

    def is_expired(self):
        """Check if the medicine has expired"""
        return datetime.utcnow() > self.expiry_at if self.expiry_at else False
    
# Medicine log model
class MedicineLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    medicine_id = db.Column(db.String(36), db.ForeignKey('medicine.id'), nullable=False)
    is_taken = db.Column(db.Boolean, default=False)  # True if medicine was taken
    created_at = db.Column(DateTime(), default=func.now()) 
    updated_at = db.Column(DateTime(), onupdate=func.now())