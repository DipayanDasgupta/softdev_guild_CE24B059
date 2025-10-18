# ai_video_generator/scripts/step_03b_generate_avatar_video.py
import os
import requests
import time
from dotenv import load_dotenv
from .config import ASSETS_DIR

# --- V2 Goal Implemented: Prioritize external audio, fallback to male TTS, and use 'stitch: true' ---

load_dotenv()
D_ID_API_KEY = os.getenv("D_ID_API_KEY")
D_ID_BASE_URL = "https://api.d-id.com"

def check_credits(auth_tuple):
    """Helper function to check available D-ID credits."""
    try:
        response = requests.get(
            f"{D_ID_BASE_URL}/credits",
            auth=auth_tuple,
            headers={"accept": "application/json"}
        )
        response.raise_for_status()
        credits_data = response.json()
        print(f"D-ID Credits Info: {credits_data}")
        # Handle different credit response formats
        remaining_credits = credits_data.get("remaining", 0)
        if not remaining_credits and "credits" in credits_data:
            remaining_credits = sum(credit.get("remaining", 0) for credit in credits_data.get("credits", []))
        return remaining_credits
    except requests.exceptions.RequestException as e:
        print(f"Error checking D-ID credits: {e}")
        if e.response is not None:
            print(f"D-ID Response: {e.response.text}")
        return 0

def upload_image(auth_tuple, image_path):
    """Helper function to upload a presenter image to D-ID."""
    print(f"Uploading presenter image: {image_path}")
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} does not exist.")
        return None
    try:
        file_ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"
        with open(image_path, "rb") as image_file:
            files = {"image": (os.path.basename(image_path), image_file, mime_type)}
            response = requests.post(
                f"{D_ID_BASE_URL}/images",
                auth=auth_tuple,
                files=files,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            image_url = response.json().get("url")
            print(f"Image uploaded successfully. URL: {image_url}")
            return image_url
    except requests.exceptions.RequestException as e:
        print(f"Error uploading image to D-ID: {e}")
        if e.response is not None:
            print(f"D-ID Response: {e.response.text}")
        return None

def upload_audio(auth_tuple, audio_path):
    """Helper function to upload an audio file to D-ID."""
    print(f"Uploading pre-generated audio: {audio_path}")
    if not os.path.exists(audio_path):
        print(f"Error: Audio file {audio_path} does not exist.")
        return None
    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": (os.path.basename(audio_path), audio_file, "audio/mpeg")}
            response = requests.post(
                f"{D_ID_BASE_URL}/audios",
                auth=auth_tuple,
                files=files,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            audio_url = response.json().get("url")
            print(f"Audio uploaded successfully. URL: {audio_url}")
            return audio_url
    except requests.exceptions.RequestException as e:
        print(f"Error uploading audio to D-ID: {e}")
        if e.response is not None:
            print(f"D-ID Response: {e.response.text}")
        return None

def generate_avatar_video(script_text: str, audio_path: str = None, output_filename: str = "avatar_video.mp4", custom_presenter_filename: str = None) -> str:
    print("Generating lip-synced avatar video with D-ID...")
    if not D_ID_API_KEY or ":" not in D_ID_API_KEY:
        print("Error: D_ID_API_KEY is missing or invalid in .env file.")
        return None
    
    auth_user, auth_pass = D_ID_API_KEY.split(":", 1)
    auth_tuple = (auth_user, auth_pass)

    if check_credits(auth_tuple) <= 0:
        print("Error: No D-ID credits available.")
        return None

    # Determine presenter image source URL
    source_url = None
    if custom_presenter_filename:
        image_path = os.path.join(ASSETS_DIR, custom_presenter_filename)
        source_url = upload_image(auth_tuple, image_path)
    
    if not source_url:
        print("Custom presenter not used or failed. Using default presenter.jpg.")
        default_image_path = os.path.join(ASSETS_DIR, "presenter.jpg")
        source_url = upload_image(auth_tuple, default_image_path)
    
    if not source_url:
        print("Error: Failed to upload any presenter image.")
        return None

    # --- NEW AUDIO LOGIC ---
    # 1. Prioritize using the pre-generated audio file (from ElevenLabs)
    script_payload = None
    if audio_path and os.path.exists(audio_path):
        print("High-quality audio file found. Uploading to D-ID.")
        audio_url = upload_audio(auth_tuple, audio_path)
        if audio_url:
            script_payload = {
                "type": "audio",
                "audio_url": audio_url
            }
        else:
            print("Warning: Failed to upload audio. Falling back to D-ID TTS.")
    
    # 2. If no pre-generated audio, fall back to D-ID's text-to-speech with a male voice
    if not script_payload:
        print("No pre-generated audio. Using D-ID's built-in TTS with a male voice.")
        script_payload = {
            "type": "text",
            "input": script_text,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-GuyNeural" # Fallback male voice
            }
        }

    # --- NEW PAYLOAD CONFIGURATION ---
    # Create the main talk payload
    payload = {
        "source_url": source_url,
        "script": script_payload,
        "config": {
            "stitch": True  # <<< IMPROVEMENT 1: Get a clean video for layering
        }
    }
    
    # Create the talk
    try:
        response = requests.post(
            f"{D_ID_BASE_URL}/talks",
            json=payload,
            auth=auth_tuple,
            headers={"accept": "application/json", "content-type": "application/json"}
        )
        response.raise_for_status()
        talk_id = response.json().get("id")
        print(f"Successfully created D-ID talk job with ID: {talk_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating D-ID talk job: {e}")
        if e.response is not None:
            print(f"D-ID Response: {e.response.text}")
        return None

    # Poll for completion
    for _ in range(30):  # Poll for up to 5 minutes (30 * 10s)
        print("Waiting for talk job to complete...")
        time.sleep(10)
        try:
            response = requests.get(
                f"{D_ID_BASE_URL}/talks/{talk_id}",
                auth=auth_tuple,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            status = data.get("status")

            if status == "done":
                video_url = data.get("result_url")
                print(f"Video ready! Downloading from: {video_url}")
                video_response = requests.get(video_url)
                video_response.raise_for_status()
                
                output_path = os.path.join(ASSETS_DIR, output_filename)
                with open(output_path, "wb") as f:
                    f.write(video_response.content)
                print(f"Avatar video saved locally to: {output_path}")
                return output_path
                
            elif status in ["error", "rejected"]:
                print(f"Talk job failed. Status: {status}. Details: {data.get('result', 'N/A')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error polling talk job: {e}")
            return None
            
    print("Timeout: Talk job did not complete in time.")
    return None