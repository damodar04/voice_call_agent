from flask import Flask, request, Response, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import sqlite3
import os
from datetime import datetime
from elevenlabs import ElevenLabs
from twilio_handler import TwilioHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Load Environment Variables ===
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# === Flask Setup ===
app = Flask(__name__)

# === Twilio Handler Setup ===
try:
    twilio_handler = TwilioHandler()
except Exception as e:
    logger.error(f"Failed to initialize Twilio handler: {e}")
    twilio_handler = None

# === SQLite Setup ===
DB_FILE = 'edc_responses.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                dob TEXT,
                email TEXT,
                start_date TEXT,
                course TEXT,
                intent TEXT,
                response TEXT,
                call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add table for call tracking
        conn.execute('''
            CREATE TABLE IF NOT EXISTS call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT UNIQUE,
                to_number TEXT,
                from_number TEXT,
                status TEXT,
                direction TEXT,
                duration INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

# === Helper: Save to DB ===
def save_response(intent, field, value):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO users (intent, response) VALUES (?, ?)", (intent, f"{field}:{value}"))

# === Helper: Save Call Log ===
def save_call_log(call_sid, to_number, from_number, status, direction, duration=None, start_time=None, end_time=None):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO call_logs 
            (call_sid, to_number, from_number, status, direction, duration, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (call_sid, to_number, from_number, status, direction, duration, start_time, end_time))

# === Helper: ElevenLabs TTS ===
def eleven_tts(text):
    try:
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        audio = client.generate(text=text, voice="Rachel")
        with open("static/response.mp3", "wb") as f:
            f.write(audio)
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")

# === Outbound Call Endpoint ===
@app.route("/make-call", methods=["POST"])
def make_outbound_call():
    """Endpoint to initiate outbound calls"""
    try:
        data = request.get_json()
        to_number = data.get('to_number')
        
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        if not twilio_handler:
            return jsonify({'error': 'Twilio handler not initialized'}), 500
        
        # Make the outbound call
        call_info = twilio_handler.make_outbound_call(to_number)
        
        # Save initial call log
        save_call_log(
            call_sid=call_info['sid'],
            to_number=call_info['to'],
            from_number=call_info['from'],
            status=call_info['status'],
            direction='outbound'
        )
        
        logger.info(f"Outbound call initiated: {call_info}")
        return jsonify(call_info), 200
        
    except Exception as e:
        logger.error(f"Error making outbound call: {e}")
        return jsonify({'error': str(e)}), 500

# === Call Status Webhook ===
@app.route("/call-status", methods=["POST"])
def call_status_webhook():
    """Handle call status updates from Twilio"""
    try:
        call_sid = request.values.get('CallSid')
        call_status = request.values.get('CallStatus')
        to_number = request.values.get('To')
        from_number = request.values.get('From')
        call_duration = request.values.get('CallDuration')
        
        logger.info(f"Call status update - SID: {call_sid}, Status: {call_status}")
        
        # Update call log
        save_call_log(
            call_sid=call_sid,
            to_number=to_number,
            from_number=from_number,
            status=call_status,
            direction='outbound' if to_number != TWILIO_NUMBER else 'inbound',
            duration=call_duration,
            start_time=datetime.now() if call_status == 'in-progress' else None,
            end_time=datetime.now() if call_status in ['completed', 'failed', 'busy', 'no-answer'] else None
        )
        
        return Response(status=200)
        
    except Exception as e:
        logger.error(f"Error handling call status: {e}")
        return Response(status=500)

# === Webhook: Voice ===
@app.route("/voice", methods=["POST"])
def voice():
    try:
        # Log incoming call details
        call_sid = request.values.get('CallSid')
        to_number = request.values.get('To')
        from_number = request.values.get('From')
        direction = request.values.get('Direction')
        
        logger.info(f"Incoming voice request - SID: {call_sid}, From: {from_number}, To: {to_number}")
        
        # Save call log for incoming calls
        if direction == 'inbound':
            save_call_log(
                call_sid=call_sid,
                to_number=to_number,
                from_number=from_number,
                status='ringing',
                direction='inbound'
            )
        
        intent = request.values.get("SpeechResult", "").lower()
        response = VoiceResponse()

        if "inquiry" in intent:
            eleven_tts("Which service are you interested in? Car beginner or heavy vehicle?")
            gather = Gather(input="speech", action="/inquiry", method="POST")
            gather.play(url="/static/response.mp3")
            response.append(gather)
        elif "register" in intent:
            eleven_tts("What is your full name?")
            gather = Gather(input="speech", action="/register_name", method="POST")
            gather.play(url="/static/response.mp3")
            response.append(gather)
        elif "reschedule" in intent:
            eleven_tts("Please say your email to find your record for rescheduling.")
            gather = Gather(input="speech", action="/reschedule", method="POST")
            gather.play(url="/static/response.mp3")
            response.append(gather)
        elif "cancel" in intent:
            eleven_tts("Please say your email to find your record for cancellation.")
            gather = Gather(input="speech", action="/cancel", method="POST")
            gather.play(url="/static/response.mp3")
            response.append(gather)
        else:
            eleven_tts("Welcome to Education Driving Center. Please say Inquiry, Register, Reschedule or Cancel.")
            gather = Gather(input="speech", action="/voice", method="POST")
            gather.play(url="/static/response.mp3")
            response.append(gather)

        return Response(str(response), mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error in voice webhook: {e}")
        response = VoiceResponse()
        response.say("I'm sorry, there was an error. Please try again later.", voice='alice')
        return Response(str(response), mimetype='text/xml')

# === Call Management Endpoints ===
@app.route("/call-status/<call_sid>", methods=["GET"])
def get_call_status(call_sid):
    """Get the status of a specific call"""
    try:
        if not twilio_handler:
            return jsonify({'error': 'Twilio handler not initialized'}), 500
        
        status = twilio_handler.get_call_status(call_sid)
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting call status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/hangup/<call_sid>", methods=["POST"])
def hangup_call(call_sid):
    """Hang up a specific call"""
    try:
        if not twilio_handler:
            return jsonify({'error': 'Twilio handler not initialized'}), 500
        
        success = twilio_handler.hangup_call(call_sid)
        return jsonify({'success': success}), 200
        
    except Exception as e:
        logger.error(f"Error hanging up call: {e}")
        return jsonify({'error': str(e)}), 500

# === Inquiry Route ===
@app.route("/inquiry", methods=["POST"])
def inquiry():
    service = request.values.get("SpeechResult", "")
    save_response("inquiry", "service", service)
    eleven_tts(f"Thanks. Would you like to register now for {service} course?")
    response = VoiceResponse()
    gather = Gather(input="speech", action="/inquiry_register", method="POST")
    gather.play(url="/static/response.mp3")
    response.append(gather)
    return Response(str(response), mimetype='text/xml')

# === Registration Flow ===
@app.route("/register_name", methods=["POST"])
def register_name():
    name = request.values.get("SpeechResult", "")
    save_response("register", "name", name)
    eleven_tts("What is your date of birth?")
    response = VoiceResponse()
    gather = Gather(input="speech", action="/register_dob", method="POST")
    gather.play(url="/static/response.mp3")
    response.append(gather)
    return Response(str(response), mimetype='text/xml')

@app.route("/register_dob", methods=["POST"])
def register_dob():
    dob = request.values.get("SpeechResult", "")
    save_response("register", "dob", dob)
    eleven_tts("What is your email address?")
    response = VoiceResponse()
    gather = Gather(input="speech", action="/register_email", method="POST")
    gather.play(url="/static/response.mp3")
    response.append(gather)
    return Response(str(response), mimetype='text/xml')

@app.route("/register_email", methods=["POST"])
def register_email():
    email = request.values.get("SpeechResult", "")
    save_response("register", "email", email)
    eleven_tts("When would you like to start your course?")
    response = VoiceResponse()
    gather = Gather(input="speech", action="/register_date", method="POST")
    gather.play(url="/static/response.mp3")
    response.append(gather)
    return Response(str(response), mimetype='text/xml')

@app.route("/register_date", methods=["POST"])
def register_date():
    date = request.values.get("SpeechResult", "")
    save_response("register", "start_date", date)
    eleven_tts("Which course do you want to start?")
    response = VoiceResponse()
    gather = Gather(input="speech", action="/register_course", method="POST")
    gather.play(url="/static/response.mp3")
    response.append(gather)
    return Response(str(response), mimetype='text/xml')

@app.route("/register_course", methods=["POST"])
def register_course():
    course = request.values.get("SpeechResult", "")
    save_response("register", "course", course)
    eleven_tts("Your registration is complete. We will contact you soon. Thank you.")
    response = VoiceResponse()
    response.play(url="/static/response.mp3")
    return Response(str(response), mimetype='text/xml')

# === Main ===
if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
