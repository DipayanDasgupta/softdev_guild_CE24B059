# scripts/step_03_generate_audio.py (Updated with the latest ElevenLabs documentation)
import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()
ASSETS_DIR = "assets"

def generate_audio(script_text: str, filename: str = "commentary.mp3") -> str:
    """
    Generates audio from a script using the ElevenLabs API and saves it.
    """
    print("Generating AI audio with ElevenLabs...")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in .env file.")
        return None

    try:
        # Initialize the ElevenLabs client, as per the latest documentation
        client = ElevenLabs(api_key=api_key)

        # --- FIX: Use the 'text_to_speech.convert' method ---
        # This is the correct method shown in the current API reference.
        # We also add the output_format parameter for consistency.
        audio_stream = client.text_to_speech.convert(
            text=script_text,
            voice_id="pNInz6obpgDQGcFmaJgB",  # A popular voice named 'Adam'. You can find other voice_ids on their site.
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128", # Specifies the output format for the audio file.
        )
        
        # Save the streamed audio data to a file
        output_path = os.path.join(ASSETS_DIR, filename)
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
            
        print(f"Audio saved successfully to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error calling ElevenLabs API: {e}")
        return None

if __name__ == '__main__':
    test_script = "Hello, this is a test of the new AI voice generation system."
    audio_path = generate_audio(test_script)
    if audio_path:
        print(f"Test audio created at: {audio_path}")