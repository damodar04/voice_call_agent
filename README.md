# voice_call_agent
An AI-powered voice call automation system that handles inbound and outbound calls, interacts with users using natural speech (powered by Twilio and ElevenLabs), and saves responses into a structured database for future actions.

🚀 Features

Handles both inbound and outbound calls.

Uses AI voice synthesis (ElevenLabs) for human-like responses.

Captures caller information such as name, email, date, and service choice.

Stores call responses in an SQLite database.

Can be integrated with WhatsApp or email follow-ups.

Supports future automation for appointment booking and feedback collection.

🧰 Tech Stack
Functionality	Tool
Voice Calling	Twilio
Text-to-Speech / Speech-to-Text	ElevenLabs API
Backend	Flask (Python)
Database	SQLite
Deployment	Render / Railway / Ngrok (local testing)
