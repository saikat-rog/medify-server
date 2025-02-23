from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from app.models import Medicine

def check_medicine_times():
    """Check if any medicine time matches the current time."""
    now = datetime.now()
    current_time = now.strftime("%H:%M")  # Format time as HH:MM

    with scheduler.app.app_context():  # Use the app context
        medicines = Medicine.query.all()
        for medicine in medicines:
            times_list = json.loads(medicine.times) if medicine.times else []
            if current_time in times_list:
                print(f"Time arrived with date: {now.date()} and time: {current_time}")

# Initialize the scheduler
scheduler = BackgroundScheduler()

def start_scheduler(app: Flask):
    """Start the background scheduler with the Flask app context."""
    scheduler.app = app  # Store app in scheduler instance
    scheduler.add_job(check_medicine_times, 'interval', minutes=1)
    scheduler.start()
    print("[DEBUG] Scheduler started successfully.") 
