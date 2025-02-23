from app.config import db
import uuid
import datetime
import json

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
    phone = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    # Relationship: A patient has multiple courses
    courses = db.relationship("Course", backref="patient", cascade="all, delete-orphan")

# Course model
class Course(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    patient_id = db.Column(db.String(36), db.ForeignKey('patient.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    # Relationship with medicines
    medicines = db.relationship("Medicine", backref="course", cascade="all, delete-orphan")

# Medicine model
class Medicine(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id'), nullable=False)  # Fixed FK
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in days
    times = db.Column(db.String(500), nullable=False)  # Store multiple times as JSON string
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    logs = db.relationship("MedicineLog", backref="medicine", cascade="all, delete-orphan")

    def set_times(self, times_list):
        """Store list of times as a JSON string"""
        self.times = json.dumps(times_list)

    def get_times(self):
        """Retrieve list of times as a Python list"""
        return json.loads(self.times) if self.times else []
    
# Medicine log model
class MedicineLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    medicine_id = db.Column(db.String(36), db.ForeignKey('medicine.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today, nullable=False)
    time_taken = db.Column(db.Time, nullable=False)  # Actual time of intake
    is_taken = db.Column(db.Boolean, default=False)  # True if medicine was taken
