import os
import json
import os
from dotenv import load_dotenv

load_dotenv()
import requests
from playwright.sync_api import sync_playwright
from .config import API_BASE_URL, ASSETS_DIR # <-- Use new config


def create_player_stat_chart(player_id: int, match_id: int = None) -> str:
    print(f"Generating animated chart video for player ID: {player_id}, match ID: {match_id}...")
    try:
        if match_id:
            response = requests.get(f"{API_BASE_URL}/players/{player_id}/matches/{match_id}/stats")
        else:
            response = requests.get(f"{API_BASE_URL}/players/{player_id}/stats")
        response.raise_for_status()
        stats = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for chart: {e}")
        raise e
    player_name = stats.get('player_name', 'Player')
    chart_data = {
        "Total Runs": stats.get('total_runs', 0) if not match_id else stats.get('runs', 0),
        "Fifties": stats.get('fifties', 0) if not match_id else (1 if 50 <= stats.get('runs', 0) < 100 else 0),
        "Hundreds": stats.get('hundreds', 0) if not match_id else (1 if stats.get('runs', 0) >= 100 else 0),
        "Matches": stats.get('matches_played', 0) if not match_id else 1
    }
    template_path = os.path.join(ASSETS_DIR, "chart_template.html")
    with open(template_path, 'r') as f:
        html_template = f.read()
    html_content = html_template.replace("{{CHART_DATA}}", json.dumps(chart_data))
    title = f"Match Performance: {player_name}" if match_id else f"Career Highlights: {player_name}"
    html_content = html_content.replace("{{CHART_TITLE}}", title)
    output_path = os.path.join(ASSETS_DIR, f"chart_animation_{player_id}_{match_id or 'career'}.mp4")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir=ASSETS_DIR,
            record_video_size={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        page.set_content(html_content)
        page.wait_for_timeout(3000)
        context.close()
        browser.close()
        temp_video_path = page.video.path()
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(temp_video_path, output_path)
    print(f"Animated chart saved successfully to: {output_path}")
    return output_path