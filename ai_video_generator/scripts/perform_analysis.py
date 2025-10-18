# ai_video_generator/scripts/perform_analysis.py
import requests
from .config import API_BASE_URL

def get_full_match_data(match_id: int):
    """Fetches all batting stats for a given match."""
    try:
        # We need a new endpoint or to adapt an existing one for full match stats.
        # For now, let's assume a hypothetical full stats endpoint.
        # Let's hit the existing match endpoint and process the data.
        response = requests.get(f"{API_BASE_URL}/matches/{match_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching full match data: {e}")
        return None

def analyze_performance(player_id: int, match_id: int) -> dict:
    """
    Computes advanced analysis of a player's performance in a given match.
    """
    print(f"Performing analysis for player {player_id} in match {match_id}...")
    analysis = {
        "contribution_percentage": 0,
        "is_top_scorer": False,
        "strike_rate_comparison": "average"
    }

    try:
        # 1. Get player's specific stats for the match
        player_stats_res = requests.get(f"{API_BASE_URL}/players/{player_id}/matches/{match_id}/stats")
        player_stats_res.raise_for_status()
        player_stats = player_stats_res.json()
        player_runs = player_stats.get('runs', 0)
        player_sr = player_stats.get('strike_rate', 0)

        # 2. Get full match data for context
        all_stats_res = requests.get(f"{API_BASE_URL}/matches/{match_id}/players")
        all_stats_res.raise_for_status()
        players_by_team = all_stats_res.json()

        team_total = 0
        all_match_runs = []
        player_team_name = ""

        # Find the player's team and calculate team total
        for team, players in players_by_team.items():
            if any(p['id'] == player_id for p in players):
                player_team_name = team
                break

        # This part requires fetching individual stats for all players to get runs, which is inefficient.
        # A better API would return runs in the /matches/{match_id}/players endpoint.
        # For now, we'll make a simplified assumption or skip complex parts.
        # Let's focus on what we can do: find top scorer.
        
        # A more robust solution would be a dedicated /matches/{match_id}/scoreboard endpoint.
        # Given the current API, this analysis is limited. Let's make a simplified top-scorer check.
        top_score = 0
        top_scorer_id = None
        
        # This is a bit inefficient due to multiple API calls, but demonstrates the logic
        all_players_flat = [p for players in players_by_team.values() for p in players]
        for p in all_players_flat:
            try:
                res = requests.get(f"{API_BASE_URL}/players/{p['id']}/matches/{match_id}/stats")
                if res.ok:
                    p_stats = res.json()
                    p_runs = p_stats.get('runs', 0)
                    if p_runs > top_score:
                        top_score = p_runs
                        top_scorer_id = p['id']
            except:
                continue

        if top_scorer_id == player_id and player_runs > 0:
            analysis["is_top_scorer"] = True
        
        # Basic strike rate analysis
        if player_sr > 180:
            analysis["strike_rate_comparison"] = "blistering"
        elif player_sr > 150:
            analysis["strike_rate_comparison"] = "excellent"
        elif player_sr < 120:
            analysis["strike_rate_comparison"] = "modest"
            
        print(f"Analysis complete: {analysis}")
        return analysis

    except Exception as e:
        print(f"Could not perform analysis: {e}")
        return analysis # Return default analysis