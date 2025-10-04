# scripts/01_generate_script.py
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Your running FastAPI server URL
API_BASE_URL = "http://127.0.0.1:8000"

def generate_commentary_script(player_id: int) -> str:
    """
    Fetches player stats and generates a commentary script using Gemini.
    """
    print(f"Fetching stats for player ID: {player_id}...")
    
    # --- Step 1: Fetch data from your own IPL API ---
    try:
        response = requests.get(f"{API_BASE_URL}/players/{player_id}/stats")
        response.raise_for_status()  # Raises an exception for 4XX or 5XX status codes
        stats = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

    player_name = stats.get('player_name', 'this player')
    print(f"Successfully fetched stats for {player_name}.")

    # --- Step 2: Create a prompt for the Gemini API ---
    prompt = f"""
    Generate a short, exciting, and energetic 30-second video script for a cricket commentary segment about {player_name}.
    Use the following statistics to highlight their career achievements:
    - Total Matches Played: {stats['matches_played']}
    - Total Runs: {stats['total_runs']}
    - Fifties: {stats['fifties']}
    - Hundreds: {stats['hundreds']}
    - Strike Rate: {stats['strike_rate']}

    The script should be engaging for social media. Do not include scene directions or camera angles, only the spoken words for the avatar.
    Make it sound like a professional sports commentator.
    """

    # --- Step 3: Call the Gemini API ---
    print("Generating commentary script with Gemini...")
    try:
        response = model.generate_content(prompt)
        script = response.text.strip()
        print("Script generated successfully.")
        return script
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

if __name__ == '__main__':
    # Example usage: Generate a script for player ID 1 (e.g., Sachin Tendulkar if he's ID 1)
    # You would replace '1' with a dynamic ID in a real application.
    commentary = generate_commentary_script(player_id=1)
    if commentary:
        print("\n--- Generated Script ---")
        print(commentary)