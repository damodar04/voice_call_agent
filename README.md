# 🗣️ Voice Call Agent (AI-Powered Call Handling System)

An AI-driven **voice call automation system** that handles both inbound and outbound calls, interacts with users naturally using speech (powered by **Twilio** and **ElevenLabs**), and securely stores all responses in a structured database.

---

## 🚀 Features

- 📞 Handles **inbound & outbound calls** using Twilio
- 🔊 Uses **ElevenLabs** for natural text-to-speech (TTS)
- 🧠 Supports **multi-turn conversations** (Inquiry → Registration → Reschedule → Cancel)
- 🗂️ Stores user responses (name, email, date, course type, etc.) in an SQLite database
- 🌐 Fully compatible with local or cloud deployment (Ngrok / Render)
- 🧩 Easily extendable to WhatsApp or email follow-ups

---

## 🧰 Tech Stack

| Functionality | Tool/Service |
|----------------|--------------|
| Voice Calling | Twilio |
| Speech-to-Text / Text-to-Speech | ElevenLabs API |
| Backend | Flask (Python) |
| Database | SQLite |
| Deployment | Ngrok / Render / Railway |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/damodar04/voice_call_agent.git
cd voice_call_agent
2. Install Dependencies
bash
Copy code
pip install -r requirements.txt
3. Create .env File
In the root directory, create a .env file with the following:

ini
Copy code
TWILIO_NUMBER=+1XXXXXXXXXX
TWILIO_SID=your_twilio_sid
TWILIO_AUTH=your_twilio_auth
ELEVENLABS_API_KEY=your_elevenlabs_api_key
4. Run the Application
bash
Copy code
python app.py
5. Expose Locally Using Ngrok
bash
Copy code
ngrok http 5000
Copy the https URL provided by ngrok (example: https://yourname.ngrok-free.app).

🔁 Twilio Configuration
✅ For Inbound Calls:
Go to your Twilio Console → Phone Numbers → Active Number

Under Voice & Fax → A CALL COMES IN, select Webhook

Paste your ngrok URL + /voice

arduino
Copy code
https://yourname.ngrok-free.app/voice
📤 For Outbound Calls:
In your Python code, trigger calls like:

python
Copy code
from twilio.rest import Client
client = Client(account_sid, auth_token)
call = client.calls.create(
    to="+91XXXXXXXXXX",
    from_="+1XXXXXXXXXX",
    url="https://yourname.ngrok-free.app/voice"
)
🗂️ Database Structure
The system automatically creates a SQLite database (responses.db) with stored user inputs:

Field	Description
id	Unique ID
name	User’s name
email	User’s email
date_of_birth	User’s DOB
course_type	Service/course requested
start_date	Preferred start date
timestamp	When data was captured

🔮 Future Enhancements
🌐 Web dashboard to view call logs & analytics

💬 WhatsApp / SMS follow-up integration

📅 Auto-scheduler for appointment confirmation

🤖 Integration with CRM for full automation

👨‍💻 Author
Damodar Bhawsar
AI & Automation Developer
Email : damodar.7974@gmail.com







