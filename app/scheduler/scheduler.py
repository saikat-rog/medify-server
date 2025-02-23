from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, Response
from app.models import Medicine, Patient
import os
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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
            times_list = json.loads(medicine.times) if medicine.times else []
            if current_time in times_list:
                print(f"Calling patient for medicine reminder at {now.date()} {current_time}")
                
                patient = Patient.query.get(medicine.course.patient_id)
                if not patient:
                    print("Patient not found")
                    continue

                call = client.calls.create(
                    url=f"{os.getenv('SERVER_URI')}/twiml?patient_id={patient.id}&medicine_id={medicine.id}",
                    to="+918334066167",
                    from_="+12765799954"
                )
                print(f"Call initiated: {call.sid}")

@app.route("/twiml", methods=["GET", "POST"])
def twiml():
    """Generate TwiML dynamically based on medicine and patient details."""
    patient_id = request.args.get("patient_id")
    medicine_id = request.args.get("medicine_id")

    patient = Patient.query.get(patient_id)
    medicine = Medicine.query.get(medicine_id)
    
    if not patient or not medicine:
        return Response("Invalid request", status=400)

    response = VoiceResponse()
    gather = response.gather(num_digits=1, action=f"/handle_response?patient_id={patient.id}&medicine_id={medicine.id}", method="POST")
    
    gather.say(f"Hello, this is your medicine reminder. Please take your {medicine.name}. Press 1 to confirm.")

    response.say("We did not receive any input. Goodbye.")
    return Response(str(response), mimetype="text/xml")

@app.route("/handle_response", methods=["POST"])
def handle_response():
    """Handle user keypress and call APIs accordingly."""
    digit_pressed = request.form.get("Digits")
    patient_id = request.args.get("patient_id")
    medicine_id = request.args.get("medicine_id")

    response = VoiceResponse()

    if digit_pressed == "1":
        response.say("Thank you. Your medicine intake has been recorded.")
    else:
        response.say("Invalid input. Goodbye.")

    return Response(str(response), mimetype="text/xml")

# Initialize the scheduler
scheduler = BackgroundScheduler()

def start_scheduler(app: Flask):
    """Start the background scheduler with the Flask app context."""
    scheduler.app = app
    scheduler.add_job(check_medicine_times, 'interval', seconds=5)
    scheduler.start()
    print("[DEBUG] Scheduler started successfully.")
