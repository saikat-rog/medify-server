from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, Response, Blueprint
from app.models import Medicine, Patient, MedicineLog
import os
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from app.config import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

twilio_bp = Blueprint('twilio', __name__)

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

def check_medicine_times():
    """Check if any medicine time matches the current time and initiate a call."""
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    with scheduler.app.app_context():
        medicines = Medicine.query.all()
        for medicine in medicines:
            print(f"eXP: {medicine.is_expired()}")
            if medicine.is_expired():  # Skip expired medicines
                continue
            
            # Get times for mediines not expired
            times_list = json.loads(medicine.times) if medicine.times else []
            
            if current_time in times_list:
                
                print(f"Calling patient for medicine reminder at {now.date()} {current_time}")
                
                patient = Patient.query.get(medicine.course.patient_id)
                if not patient:
                    print("Patient not found")
                    continue

                call = client.calls.create(
                    url=f"{os.getenv('SERVER_URI')}/twilio/twiml?patient_id={patient.id}&medicine_id={medicine.id}",
                    to="+918334066167",
                    from_="+12765799954"
                    # to="+917586914646", //soumik
                    # from_="+15396664952" //soumik
                )
                print(f"Call initiated: {call.sid}")

@twilio_bp.route('/twiml', methods=['POST'])
def twiml():
    """Generate TwiML dynamically based on medicine and patient details."""
    patient_id = request.args.get("patient_id")
    medicine_id = request.args.get("medicine_id")

    patient = Patient.query.get(patient_id)
    medicine = Medicine.query.get(medicine_id)
    
    if not patient or not medicine:
        return Response("Invalid request", status=400)

    response = VoiceResponse()
    gather = response.gather(num_digits=1, action=f"{os.getenv('SERVER_URI')}/twilio/handle_ivr_response?patient_id={patient.id}&medicine_id={medicine.id}", method="POST")
    
    gather.say(f"Hello, this is your medicine reminder. Please take your {medicine.name}. Press 1 to confirm.")

    response.say("We did not receive any input. Goodbye.")
    return Response(str(response), mimetype="text/xml")

@twilio_bp.route("/handle_ivr_response", methods=["POST"])
def handle_response():
    """Handle user keypress and call APIs accordingly."""
    digit_pressed = request.form.get("Digits")
    patient_id = request.args.get("patient_id")
    medicine_id = request.args.get("medicine_id")

    response = VoiceResponse()

    if digit_pressed == "1":
        new_medicine_log = MedicineLog(
            medicine_id=medicine_id,
            is_taken=True
        )
        
        db.session.add(new_medicine_log)
        db.session.commit()
        
        response.say("Thank you. Your medicine intake has been recorded.")
    else:
        new_medicine_log = MedicineLog(
            medicine_id=medicine_id,
            is_taken=False
        )
        
        db.session.add(new_medicine_log)
        db.session.commit()
        response.say("Invalid input. Goodbye.")

    return Response(str(response), mimetype="text/xml")

# Initialize the scheduler
scheduler = BackgroundScheduler()

def start_scheduler(app: Flask):
    """Start the background scheduler with the Flask app context."""
    scheduler.app = app
    scheduler.add_job(check_medicine_times, 'cron', second=0, id='medicine_checker', replace_existing=True)
    scheduler.start()
    print("[DEBUG] Scheduler started successfully.")
