import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

from src.data_handler import load_leads, save_leads

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Twilio config
TWILIO_SID    = os.getenv("TWILIO_SID")
TWILIO_TOKEN  = os.getenv("TWILIO_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
BASE_URL      = os.getenv("BASE_URL")

client = Client(TWILIO_SID, TWILIO_TOKEN)
app = FastAPI()

# In‑memory copy; reloaded on server restart
leads = load_leads()

@app.post("/initiate/{lead_id}")
def initiate_call(lead_id: int):
    """
    Trigger an outbound call to the specified lead.
    """
    lead = next((l for l in leads if int(l["LeadID"]) == lead_id), None)
    if not lead:
        return {"error": "Lead not found"}
    
    from voice_generator import generate_greeting_audio
    audio_path = generate_greeting_audio(lead)
    public_audio_url = f"{BASE_URL}/{audio_path}"
    
    call = client.calls.create(
        to=lead["PhoneNumber"],
        from_=TWILIO_NUMBER,
        url=f"{BASE_URL}/twiml/{lead_id}"
    )
    return {"sid": call.sid}

@app.post("/twiml/{lead_id}")
def twiml(lead_id: int):
    """
    Serve TwiML: play the generated MP3 and gather 1 digit.
    """
    resp = VoiceResponse()
    audio_url = f"{BASE_URL}/audios/{lead_id}.mp3"
    gather = Gather(num_digits=1, action=f"/gather/{lead_id}", timeout=8)
    gather.play(audio_url)
    resp.append(gather)
    resp.say("No input received. Goodbye.")
    return Response(str(resp), media_type="application/xml")

@app.post("/gather/{lead_id}")
async def gather(lead_id: int, request: Request):
    """
    Receive DTMF, map to slot, update data, and confirm.
    """
    form = await request.form()
    digit = form.get("Digits", "")
    idx = int(digit) - 1 if digit.isdigit() else -1

    lead = next((l for l in leads if int(l["LeadID"]) == lead_id), None)
    slots = [s.strip() for s in lead["AvailableSlots"].split(";")]
    chosen = slots[idx] if 0 <= idx < len(slots) else None

    # Update lead record
    lead["BookedSlot"]  = chosen or ""
    lead["Status"]      = "Booked" if chosen else "No‑Answer"
    lead["BookingTime"] = __import__("datetime").datetime.utcnow().isoformat()
    save_leads(leads)

    resp = VoiceResponse()
    if chosen:
        resp.say(f"Your appointment is set for {chosen}. Thank you!")
    else:
        resp.say("Invalid choice, exiting.")
    return Response(str(resp), media_type="application/xml")
