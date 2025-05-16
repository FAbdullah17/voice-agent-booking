import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))
API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")  # e.g., 21m00Tcm4TlvDq8ikWAM

client = ElevenLabs(api_key=API_KEY)

def list_available_voices() -> None:
    """
    Prints all voices available in your ElevenLabs account.
    Run this once to verify VOICE_ID.
    """
    try:
        response = client.voices.get_all()
        voices = response.voices
        print("Available voices:")
        for v in voices:
            print(f"  {v.voice_id} — {v.name}")
    except ApiError as e:
        print(f"Error fetching voices: {e}")

def generate_greeting_audio(lead: dict) -> str:
    """
    Creates a personalized MP3 greeting with slot options.
    Returns the local file path in 'audios/'.
    """
    if not VOICE_ID:
        raise RuntimeError("VOICE_ID is not set in the .env file.")

    name = lead.get("Name", "there")
    slots = [s.strip() for s in lead.get("AvailableSlots", "").split(";") if s.strip()]
    if not slots:
        raise ValueError("No AvailableSlots provided for the lead.")

    prompts = [f"Press {i+1} for {slot}" for i, slot in enumerate(slots)]
    text = f"Hello {name}, to book an appointment, " + ", ".join(prompts) + "."

    try:
        audio_stream = client.text_to_speech.convert_as_stream(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
    except ApiError as e:
        raise RuntimeError(f"TTS generation failed ({e.status_code}): {e.body}") from e

    audio_bytes = b"".join(audio_stream)
    os.makedirs("audios", exist_ok=True)
    filename = f"audios/{lead.get('LeadID', 'unknown')}.mp3"
    with open(filename, "wb") as audio_file:
        audio_file.write(audio_bytes)

    return filename

if __name__ == "__main__":
    list_available_voices()

    test_lead = {
        "LeadID": "test",
        "Name": "Test User",
        "AvailableSlots": "Mon 3 PM;Tue 4 PM;Wed 1 PM"
    }
    filepath = generate_greeting_audio(test_lead)
    print(f"Generated audio file at: {filepath}")
