import os
import requests
import os
from dotenv import load_dotenv

load_dotenv()
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def generate_commentary_script(player_id: int, match_id: int = None, tone: str = "energetic") -> str:
    print(f"Fetching stats for player ID: {player_id}, match ID: {match_id}, tone: {tone}...")
    try:
        if match_id:
            response = requests.get(f"{API_BASE_URL}/players/{player_id}/matches/{match_id}/stats")
        else:
            response = requests.get(f"{API_BASE_URL}/players/{player_id}/stats")
        response.raise_for_status()
        stats = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        raise e
    player_name = stats.get('player_name', 'this player')
    print(f"Successfully fetched stats for {player_name}.")
    if match_id:
        prompt = f"""
        Generate a short, {tone}, 30-second video script for a cricket commentary segment about {player_name}'s performance in a specific match (Match ID: {match_id}).
        Use the following statistics:
        - Runs Scored: {stats.get('runs', 0)}
        - Balls Faced: {stats.get('balls_faced', 0)}
        - Strike Rate: {stats.get('strike_rate', 0)}
        The script should be engaging for social media, sound like a professional sports commentator, and reflect the selected tone ({tone}). Do not include scene directions or camera angles, only the spoken words for the avatar.
        """
    else:
        prompt = f"""
        Generate a short, {tone}, 30-second video script for a cricket commentary segment about {player_name}'s career.
        Use the following statistics:
        - Total Matches Played: {stats.get('matches_played', 0)}
        - Total Runs: {stats.get('total_runs', 0)}
        - Fifties: {stats.get('fifties', 0)}
        - Hundreds: {stats.get('hundreds', 0)}
        - Strike Rate: {stats.get('strike_rate', 0)}
        The script should be engaging for social media, sound like a professional sports commentator, and reflect the selected tone ({tone}). Do not include scene directions or camera angles, only the spoken words for the avatar.
        """
    print(f"Generating {tone} commentary script with Gemini...")
    try:
        response = model.generate_content(prompt)
        script = response.text.strip()
        print("Script generated successfully.")
        return script
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None