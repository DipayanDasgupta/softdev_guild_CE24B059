# ai_video_generator/scripts/step_01_generate_script.py
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from .config import API_BASE_URL
# --- NEW: Import the analysis function ---
from .perform_analysis import analyze_performance

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash') # Using a more capable model is good for this

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
        return None

    player_name = stats.get('player_name', 'this player')
    print(f"Successfully fetched stats for {player_name}.")

    prompt = ""
    if match_id:
        # --- NEW: Perform analysis for match-specific commentary ---
        analysis = analyze_performance(player_id, match_id)
        prompt = f"""
        Generate a short, {tone}, 30-second video script for a professional cricket commentary segment about {player_name}'s performance in Match ID {match_id}.
        
        **Core Statistics:**
        - Runs Scored: {stats.get('runs', 0)}
        - Balls Faced: {stats.get('balls_faced', 0)}
        - Strike Rate: {stats.get('strike_rate', 0)}

        **Key Analytical Points:**
        - Was this the top score of the match? {'Yes, a match-winning performance!' if analysis['is_top_scorer'] else 'No, but a solid contribution.'}
        - How was their scoring pace? Their strike rate was {analysis['strike_rate_comparison']}.

        **Instructions:**
        You are a world-class cricket analyst. Do NOT just list the stats. Weave them into a compelling narrative. Start with a hook, explain the impact of the performance using the analytical points, and conclude with a summary statement. The tone should be {tone}.
        The script must only contain the spoken words for the avatar. No scene directions.
        """
    else: # Career stats prompt remains the same
        prompt = f"""
        Generate a short, {tone}, 30-second video script for a cricket commentary segment about {player_name}'s illustrious career.
        Use these career statistics: Total Matches: {stats.get('matches_played', 0)}, Total Runs: {stats.get('total_runs', 0)}, Fifties: {stats.get('fifties', 0)}, Hundreds: {stats.get('hundreds', 0)}, Career Strike Rate: {stats.get('strike_rate', 0)}.
        Make it sound engaging for social media. The script must only contain the spoken words for the avatar.
        """

    print("Generating advanced commentary script with Gemini...")
    try:
        response = model.generate_content(prompt)
        script = response.text.strip().replace("*", "") # Clean up markdown
        print("Script generated successfully.")
        return script
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None