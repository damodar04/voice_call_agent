import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioHandler:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing required Twilio environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def make_outbound_call(self, to_number, webhook_url=None):
        """
        Make an outbound call to the specified number
        
        Args:
            to_number (str): The phone number to call
            webhook_url (str): The webhook URL for call handling (optional)
        
        Returns:
            dict: Call information including SID and status
        """
        try:
            # Default webhook URL if not provided
            if not webhook_url:
                webhook_url = f"{os.getenv('BASE_URL', 'http://localhost:5000')}/voice"
            
            logger.info(f"Making outbound call to {to_number}")
            
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=webhook_url,
                status_callback=f"{os.getenv('BASE_URL', 'http://localhost:5000')}/call-status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )
            
            logger.info(f"Outbound call initiated with SID: {call.sid}")
            return {
                'sid': call.sid,
                'status': call.status,
                'to': call.to,
                'from': call.from_
            }
            
        except Exception as e:
            logger.error(f"Error making outbound call: {str(e)}")
            raise
    
    def get_call_status(self, call_sid):
        """
        Get the current status of a call
        
        Args:
            call_sid (str): The call SID to check
        
        Returns:
            dict: Call status information
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                'sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time,
                'end_time': call.end_time
            }
        except Exception as e:
            logger.error(f"Error getting call status: {str(e)}")
            raise
    
    def hangup_call(self, call_sid):
        """
        Hang up an active call
        
        Args:
            call_sid (str): The call SID to hang up
        
        Returns:
            bool: True if successful
        """
        try:
            call = self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} hung up successfully")
            return True
        except Exception as e:
            logger.error(f"Error hanging up call: {str(e)}")
            raise
    
    def create_voice_response(self, message=None, gather_action=None, gather_method='POST'):
        """
        Create a TwiML voice response
        
        Args:
            message (str): Message to speak
            gather_action (str): Action URL for gather
            gather_method (str): HTTP method for gather
        
        Returns:
            str: TwiML response as string
        """
        response = VoiceResponse()
        
        if message:
            response.say(message, voice='alice')
        
        if gather_action:
            gather = response.gather(
                input='speech',
                action=gather_action,
                method=gather_method,
                timeout=10,
                speech_timeout='auto'
            )
            # Add a fallback message if no speech is detected
            gather.say("I didn't hear anything. Please try again.", voice='alice')
        
        return str(response)
