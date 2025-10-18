import os
import requests
import time
from dotenv import load_dotenv
from .config import ASSETS_DIR

load_dotenv()
D_ID_API_KEY = os.getenv("D_ID_API_KEY")
D_ID_BASE_URL = "https://api.d-id.com"

def check_credits(auth_tuple):
    try:
        response = requests.get(
            f"{D_ID_BASE_URL}/credits",
            auth=auth_tuple,
            headers={"accept": "application/json"}
        )
        response.raise_for_status()
        credits_data = response.json()
        print(f"Credits available: {credits_data}")
        remaining_credits = credits_data.get("remaining", 0)
        if not remaining_credits and "credits" in credits_data:
            remaining_credits = sum(credit.get("remaining", 0) for credit in credits_data.get("credits", []))
        return remaining_credits
    except requests.exceptions.RequestException as e:
        print(f"Error checking credits: {e}")
        if e.response is not None:
            print(f"D-ID Response: {e.response.text}")
        return 0

def upload_image(auth_tuple, image_path):
    print(f"Uploading image: {image_path}")
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} does not exist.")
        return None
    try:
        with open(image_path, "rb") as image_file:
            files = {"image": (os.path.basename(image_path), image_file, "image/jpeg")}
            response = requests.post(
                f"{D_ID_BASE_URL}/clips/images",  # Updated endpoint
                auth=auth_tuple,
                files=files,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            image_data = response.json()
            image_url = image_data.get("url")
            if not image_url:
                print("Error: No URL returned from image upload.")
                return None
            print(f"Image uploaded successfully. URL: {image_url}")
            return image_url
    except requests.exceptions.RequestException as e:
        print(f"Error uploading image: {e}")
        if e.response is not None:
            print(f"D-ID Response: {e.response.text}")
        return None

def generate_avatar_video(script_text: str, output_filename: str = "avatar_video.mp4", custom_presenter_filename: str = None) -> str:
    print("Generating lip-synced avatar video with D-ID...")
    print(f"DEBUG: Script text received: {repr(script_text)}")
    if not D_ID_API_KEY or ":" not in D_ID_API_KEY:
        print("Error: D_ID_API_KEY is missing or in the wrong format.")
        return None
    auth_user, auth_pass = D_ID_API_KEY.split(":", 1)
    auth_tuple = (auth_user, auth_pass)
    
    # Check credits
    credits = check_credits(auth_tuple)
    if credits <= 0:
        print("Error: No credits available in D-ID account. Please check your account status or upgrade.")
        return None
    print(f"Proceeding with {credits} credits available.")
    
    # Try custom presenter image first, fall back to default if needed
    source_url = None
    if custom_presenter_filename:
        image_path = os.path.join(ASSETS_DIR, custom_presenter_filename)
        source_url = upload_image(auth_tuple, image_path)
    
    if not source_url:
        print("Custom presenter upload failed or not provided. Falling back to default presenter image.")
        image_path = os.path.join(ASSETS_DIR, "presenter.jpg")
        source_url = upload_image(auth_tuple, image_path) if os.path.exists(image_path) else None
    
    if not source_url:
        print("Error: Failed to upload any presenter image. Aborting.")
        return None
    
    # Create talk job
    print("Creating talk job with text-based script...")
    payload = {
        "source_url": source_url,
        "script": {
            "type": "text",
            "input": script_text,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural"
            }
        },
        "config": {
            "stitch": True,
            "fluent": True,
            "pad_audio": 0.0
        }
    }
    
    max_retries = 3
    talk_id = None
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} to create talk job...")
            response = requests.post(
                f"{D_ID_BASE_URL}/clips",  # Updated endpoint
                json=payload,
                auth=auth_tuple,
                headers={"accept": "application/json", "content-type": "application/json"}
            )
            response.raise_for_status()
            talk_id = response.json().get("id")
            print(f"Created talk job with ID: {talk_id}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Error creating talk job (Attempt {attempt + 1}): {e}")
            if e.response is not None:
                print(f"D-ID Response: {e.response.text}")
            if attempt + 1 == max_retries:
                print("Max retries reached. Aborting.")
                return None
            time.sleep(2)
    
    if not talk_id:
        print("Failed to create talk job after all attempts.")
        return None
    
    # Poll for completion
    for attempt in range(30):
        print(f"Waiting for talk job to complete... (Attempt {attempt + 1}/30)")
        time.sleep(10)
        try:
            response = requests.get(
                f"{D_ID_BASE_URL}/clips/{talk_id}",  # Updated endpoint
                auth=auth_tuple,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "done":
                video_url = data.get("result_url")
                if not video_url:
                    print("Error: No result_url found in response.")
                    print(f"D-ID Response: {data}")
                    return None
                print(f"Video ready! Downloading from: {video_url}")
                video_response = requests.get(video_url)
                video_response.raise_for_status()
                output_path = os.path.join(ASSETS_DIR, output_filename)
                with open(output_path, "wb") as f:
                    f.write(video_response.content)
                print(f"Video saved locally to: {output_path}")
                return output_path
            elif data.get("status") in ["error", "rejected"]:
                print(f"Talk job failed. Status: {data.get('status')}. Details: {data.get('result', 'No error details provided')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error polling talk job: {e}")
            if e.response is not None:
                print(f"D-ID Response: {e.response.text}")
            return None
    print("Timeout: Talk job did not complete in time.")
    return None