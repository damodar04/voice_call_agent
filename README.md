# Voice Call Agent - Inbound And Outbound Call System

This application provides both inbound and outbound call functionality using Twilio and ElevenLabs for voice synthesis.

## Features

- **Inbound Calls**: Handle incoming calls with voice recognition and automated responses
- **Outbound Calls**: Initiate outbound calls with proper call lifecycle management
- **Call Tracking**: Log all call activities and status updates
- **Voice Synthesis**: Use ElevenLabs for high-quality text-to-speech
- **Database Storage**: Store user responses and call logs in SQLite

## Prerequisites

- Python 3.7+
- Twilio Account (Account SID, Auth Token, Phone Number)
- ElevenLabs API Key
- ngrok or similar for webhook exposure (for production)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=your_twilio_phone_number

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Application Configuration
BASE_URL=https://your-ngrok-url.ngrok.io
```

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** (see above)

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Expose your local server** (for webhooks):
   ```bash
   ngrok http 5000
   ```

5. **Update your BASE_URL** in the `.env` file with the ngrok URL

## Usage

### Making Outbound Calls

#### Using the API Endpoint

```bash
curl -X POST http://localhost:5000/make-call \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+1234567890"}'
```

#### Using the Test Script

```bash
python test_outbound_call.py
```

### Call Management

- **Get Call Status**: `GET /call-status/<call_sid>`
- **Hang Up Call**: `POST /hangup/<call_sid>`

### Webhook Endpoints

- **Voice Webhook**: `/voice` - Handles incoming and outbound call voice interactions
- **Call Status Webhook**: `/call-status` - Receives call status updates from Twilio

## Twilio Configuration

### Webhook URLs

In your Twilio console, configure the following webhook URLs:

1. **Voice Webhook URL**: `https://your-ngrok-url.ngrok.io/voice`
2. **Status Callback URL**: `https://your-ngrok-url.ngrok.io/call-status`

### Phone Number Configuration

1. Go to your Twilio Console
2. Navigate to Phone Numbers → Manage → Active numbers
3. Click on your phone number
4. Set the **Voice Configuration**:
   - **Webhook URL**: `https://your-ngrok-url.ngrok.io/voice`
   - **HTTP Method**: POST

## Database Schema

### Users Table
Stores user registration and inquiry data:
- `id`: Primary key
- `name`: User's full name
- `dob`: Date of birth
- `email`: Email address
- `intent`: User's intent (inquiry, register, etc.)
- `response`: User's response
- `call_time`: Timestamp of the call

### Call Logs Table
Tracks all call activities:
- `id`: Primary key
- `call_sid`: Twilio call SID
- `to_number`: Destination phone number
- `from_number`: Source phone number
- `status`: Call status (initiated, ringing, in-progress, completed, etc.)
- `direction`: Call direction (inbound/outbound)
- `duration`: Call duration in seconds
- `start_time`: Call start timestamp
- `end_time`: Call end timestamp
- `created_at`: Record creation timestamp

## Troubleshooting

### Common Issues

1. **Calls being cut immediately**:
   - Check that your webhook URLs are accessible
   - Verify Twilio credentials are correct
   - Ensure your ngrok URL is updated in the environment variables
   - Check the application logs for errors

2. **Webhook not receiving requests**:
   - Verify ngrok is running and the URL is correct
   - Check that the webhook URL is properly configured in Twilio
   - Ensure your application is running on the correct port

3. **Voice synthesis not working**:
   - Verify ElevenLabs API key is correct
   - Check that the `static` directory exists and is writable
   - Review application logs for TTS errors

### Debugging

1. **Enable debug logging**:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Twilio logs**:
   - Go to Twilio Console → Monitor → Logs
   - Look for call attempts and webhook delivery status

3. **Monitor application logs**:
   - Watch the console output when running the application
   - Check for error messages and webhook requests

## API Reference

### POST /make-call
Initiates an outbound call.

**Request Body**:
```json
{
  "to_number": "+1234567890"
}
```

**Response**:
```json
{
  "sid": "CA1234567890abcdef",
  "status": "initiated",
  "to": "+1234567890",
  "from": "+0987654321"
}
```

### GET /call-status/<call_sid>
Gets the status of a specific call.

**Response**:
```json
{
  "sid": "CA1234567890abcdef",
  "status": "in-progress",
  "duration": 45,
  "start_time": "2024-01-01T12:00:00Z",
  "end_time": null
}
```

### POST /hangup/<call_sid>
Hangs up a specific call.

**Response**:
```json
{
  "success": true
}
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive credentials to version control
2. **Webhook Validation**: Consider implementing Twilio webhook signature validation
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Input Validation**: Validate phone numbers and other inputs
5. **HTTPS**: Use HTTPS in production for webhook endpoints

## Development

### Project Structure
```
edc_voice_agent/
├── app.py                 # Main Flask application
├── twilio_handler.py      # Twilio API wrapper
├── database.py           # Database operations
├── requirements.txt      # Python dependencies
├── test_outbound_call.py # Test script
├── static/              # Static files (audio)
├── templates/           # TwiML templates
└── edc_responses.db     # SQLite database
```

### Adding New Features

1. **New Voice Commands**: Add new conditions in the `/voice` route
2. **Additional Call Actions**: Extend the `TwilioHandler` class
3. **Database Operations**: Add new tables or modify existing schemas
4. **Webhook Handlers**: Create new routes for additional webhook types

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Twilio and ElevenLabs documentation
3. Check application logs for error messages
4. Verify all environment variables are set correctly


