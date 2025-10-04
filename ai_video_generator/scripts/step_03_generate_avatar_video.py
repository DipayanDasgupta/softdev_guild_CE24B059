# scripts/03_generate_avatar_video.py
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
# CONSULT HEYGEN DOCUMENTATION FOR THE CORRECT ENDPOINTS
HEYGEN_CREATE_ENDPOINT = "https://api.heygen.com/v1/video/generate" 
HEYGEN_STATUS_ENDPOINT = "https://api.heygen.com/v1/video/status"

def generate_avatar_video(script_text: str) -> str:
    """
    Submits a script to an AI avatar service and returns the video URL.
    
    NOTE: This is a simplified, conceptual implementation. You MUST consult
    your chosen API's documentation for the correct payload, headers, and
    polling logic.
    """
    print("Submitting script to AI Avatar API...")
    if not HEYGEN_API_KEY:
        print("Error: HEYGEN_API_KEY not found in .env file.")
        return None

    headers = {
        "Authorization": f"Bearer {HEYGEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # --- This payload is HYPOTHETICAL. Check your API's documentation. ---
    payload = {
        "text": script_text,
        "avatar_id": "your_chosen_avatar_id", # Or avatar configuration
        "voice_id": "your_chosen_voice_id",   # Or voice configuration
    }

    try:
        # --- Step 1: Submit the job ---
        response = requests.post(HEYGEN_CREATE_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        job_id = response.json().get("data", {}).get("video_id")
        
        if not job_id:
            print("Failed to submit video generation job.")
            return None
            
        print(f"Video generation job submitted successfully. Job ID: {job_id}")

        # --- Step 2: Poll for completion ---
        while True:
            print("Checking video status...")
            status_response = requests.get(f"{HEYGEN_STATUS_ENDPOINT}/{job_id}", headers=headers)
            status_response.raise_for_status()
            
            status_data = status_response.json().get("data", {})
            video_status = status_data.get("status")

            if video_status == "completed":
                video_url = status_data.get("video_url")
                print(f"Video generation complete! URL: {video_url}")
                return video_url
            elif video_status in ["failed", "error"]:
                print("Video generation failed.")
                return None
            
            # Wait before checking again to avoid rate limiting
            time.sleep(15)

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None

if __name__ == '__main__':
    test_script = "Hello, this is a test script for the AI avatar video generation."
    video_url = generate_avatar_video(test_script)
    if video_url:
        print(f"Received video URL: {video_url}")