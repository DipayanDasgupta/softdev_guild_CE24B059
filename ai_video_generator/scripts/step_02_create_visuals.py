# scripts/step_02_create_visuals.py
import matplotlib.pyplot as plt
import pandas as pd
import os
import requests

API_BASE_URL = "http://127.0.0.1:8000"
ASSETS_DIR = "assets"

def create_player_stat_chart(player_id: int) -> str:
    """
    Fetches player stats and creates a bar chart, saving it as a PNG.
    """
    print(f"Creating static chart with Matplotlib for player ID: {player_id}...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/players/{player_id}/stats")
        response.raise_for_status()
        stats = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for visual: {e}")
        return None

    player_name = stats.get('player_name', 'Player')
    
    chart_data = {
        "Total Runs": stats.get('total_runs', 0),
        "Fifties": stats.get('fifties', 0),
        "Hundreds": stats.get('hundreds', 0),
        "Matches": stats.get('matches_played', 0)
    }
    
    chart_series = pd.Series(chart_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    chart_series.plot(kind='bar', ax=ax, color=['skyblue', 'lightgreen', 'salmon', 'gold'])
    
    ax.set_title(f"Career Highlights: {player_name}", fontsize=16, weight='bold')
    ax.set_ylabel("Count", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=12)

    # Add value labels on top of bars
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')

    plt.tight_layout()
    
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        
    output_path = os.path.join(ASSETS_DIR, f"{player_name.replace(' ', '_')}_stats.png")
    plt.savefig(output_path)
    plt.close()
    
    print(f"Static chart saved successfully to: {output_path}")
    return output_path