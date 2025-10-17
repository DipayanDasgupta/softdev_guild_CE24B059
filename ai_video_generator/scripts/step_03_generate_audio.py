import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
ASSETS_DIR = "assets"

def generate_audio(script_text: str, filename: str = "commentary.mp3") -> str:
    print("Generating AI audio with ElevenLabs...")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in .env file.")
        return None
    try:
        client = ElevenLabs(api_key=api_key)
        audio_stream = client.text_to_speech.convert(
            text=script_text,
            voice_id="pNInz6obpgDQGcFmaJgB",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        output_path = os.path.join(ASSETS_DIR, filename)
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        print(f"Audio saved successfully to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error calling ElevenLabs API: {e}")
        return None