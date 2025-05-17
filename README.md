# 🎙️ Voice Agent Appointment Booking System

**Voice Agent Booking** is a full-stack AI-driven voice automation solution that allows you to automatically book appointments over phone calls. The system uses a Python **FastAPI** backend, **ElevenLabs** for text-to-speech generation, **Twilio** for outbound calls and DTMF input, and **ngrok** for exposing your local server to the internet. All lead data is managed via a simple CSV file, making the solution lightweight, customizable, and easy to integrate into existing workflows.

---

## 🔍 Key Features

* **Dynamic TTS Generation** using ElevenLabs API for realistic voice prompts
* **Outbound Calling & IVR** via Twilio Voice API with DTMF support
* **Automated SMS Fallback** for no-answer or failed calls using Twilio SMS API
* **CSV-Based Data Storage** for leads and appointment slots
* **Modular FastAPI Architecture** for clear separation of concerns
* **Local Tunneling** with ngrok for secure webhook testing
* **Environment-Driven Configuration** via a single `.env` file

---

## 📂 Detailed Project Structure

```
voice-agent-booking/
├── data/
│   └── leads.csv            # LeadID, Name, PhoneNumber, AvailableSlots,BookedSlot,Status,BookingTime
├── audios/                  # Generated MP3 files from ElevenLabs
├── src/
│   ├── main.py              # FastAPI app initialization & route mounting
│   ├── call_handler.py      # /voice/initiate, /voice/twiml, /voice/gather endpoints
│   ├── voice_generator.py   # generate_greeting_audio(): ElevenLabs TTS logic
│   └── data_handler.py      # load_leads(), save_leads(): CSV CRUD operations
├── .env                     # Environment variables and API keys
├── requirements.txt         # Python packages (FastAPI, Twilio, ElevenLabs, python-dotenv)
└── README.md                # This documentation file
```

---

## ⚙️ Prerequisites

* **Python 3.8+**
* **Twilio account** with voice-capable phone number and \$15.50 trial credit
* **ElevenLabs account** with free-tier TTS access
* **ngrok** (v3) for HTTP tunneling
* A **Google or SMTP** account if you wish to add email reporting (optional)

---

## 🛠️ Setup Guide

### 1. Clone & Navigate

```bash
git clone https://github.com/FAbdullah17/voice-agent-booking.git
cd voice-agent-booking
```

### 2. Python Environment

```bash
python -m venv venv
# Windows
env\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Create a `.env` file at project root with:

```dotenv
ELEVENLABS_API_KEY=<your_elevenlabs_api_key>
VOICE_ID=<your_elevenlabs_voice_id>
TWILIO_SID=<your_twilio_account_sid>
TWILIO_TOKEN=<your_twilio_auth_token>
TWILIO_NUMBER=<your_twilio_phone_number>
BASE_URL=https://<your-ngrok-subdomain>.ngrok-free.app/voice
LEADS_CSV=data/leads.csv
```

* **VOICE\_ID**: obtained from ElevenLabs dashboard under *API → Voices*
* **BASE\_URL**: will be updated after starting ngrok (see next step)

---

## 🚀 Running the Application

1. **Start FastAPI**:

   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

   * The server runs at `http://localhost:8000`

2. **Expose via ngrok**:

   ```bash
   ngrok http 8000
   ```

   * Copy the generated `https://*.ngrok-free.app` URL
   * Update `BASE_URL` in your `.env` with this URL + `/voice`

3. **Restart FastAPI** to load the new `BASE_URL`.

---

## ☎️ Twilio Webhook Configuration

In your [Twilio Console](https://console.twilio.com/):

1. **Phone Numbers → Manage → Active Numbers**
2. Select your number → **Voice & Fax**
3. Under **A Call Comes In**, set:

   * **Webhook**: `https://<your-ngrok-subdomain>.ngrok-free.app/voice/initiate/{LeadID}`
   * Method: `POST`

Replace `{LeadID}` with the numeric ID from your `leads.csv`.

---

## 📊 Data CSV Format

Path: `data/leads.csv`

| LeadID | Name       | PhoneNumber   | AvailableSlots               | BookedSlot | Status  | BookingTime |
| ------ | ---------- | ------------- | ---------------------------- | ---------- | ------- | ----------- |
| 1      | Alice Khan | +923001234567 | Mon 3 PM; Tue 4 PM; Wed 1 PM |            | Pending |             |
| 2      | Omar Lee   | +14155556666  | Fri 10 AM; Fri 2 PM          |            | Pending |             |

* **AvailableSlots**: semicolon-separated options
* **BookedSlot**, **Status**, **BookingTime** are populated automatically

---

## 🔄 Workflow Detail

1. **Initiate Call** (`POST /voice/initiate/{LeadID}`)

   * Loads lead row by ID
   * Calls `generate_greeting_audio()` to create MP3
   * Uses Twilio API to place a call pointing to `/voice/twiml/{LeadID}`

2. **Serve TwiML** (`POST /voice/twiml/{LeadID}`)

   * Returns TwiML XML to play the MP3 and gather one digit

3. **Handle DTMF** (`POST /voice/gather/{LeadID}`)

   * Reads pressed digit
   * Maps to slot index, updates CSV via `data_handler.py`
   * Responds with confirmation message
   * Optional SMS fallback on failure

---

## ⚙️ Error Handling & Logging

* **Missing Voice ID**: Raises error if `VOICE_ID` unset
* **Invalid DTMF**: Responds with error message and exits
* **Twilio API Errors**: Caught and logged; call status updated to `Failed`

---

## 🧪 Testing

* **Swagger UI**: `https://<ngrok-subdomain>.ngrok-free.app/voice/docs`
* **Trigger Call**:

  ```bash
  curl -X POST https://<ngrok-subdomain>.ngrok-free.app/voice/initiate/1
  ```

---

## 🔧 Extensibility

* **Database Integration**: Replace CSV with PostgreSQL or MongoDB
* **Multilingual Support**: Leverage ElevenLabs multilingual voices
* **Email Reporting**: Use SMTP to send daily booking summaries
* **Containerization**: Dockerize for cloud deployment

---

## 🪪 License

MIT License
