from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case

from typing import List, Dict, Any
# NEW: Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

from db import SessionLocal, engine, Base
from models import Player, Team, Match, Inning, BattingStat
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IPL Data API",
    description="An API to explore player and match statistics from the Indian Premier League.",
    version="1.1.0",  # Version bump
)

# NEW: Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5001", "http://localhost:5001"],  # Allow specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the IPL Data API. Go to /docs for an interactive API documentation."}

@app.get("/teams", response_model=List[schemas.TeamResponse], tags=["Teams"])
def get_all_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return teams

@app.get("/teams/{team_id}/players", response_model=List[schemas.PlayerResponse], tags=["Teams"])
def get_players_by_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    players = (
        db.query(Player)
        .join(BattingStat, Player.id == BattingStat.player_id)
        .join(Inning, BattingStat.inning_id == Inning.id)
        .filter(Inning.team_id == team_id)
        .distinct()
        .all()
    )
    return players

@app.get("/stats/leaderboard/{season}", response_model=List[schemas.PlayerSeasonStats], tags=["Stats"])
def get_season_leaderboard(season: int, top_n: int = 10, db: Session = Depends(get_db)):
    leaderboard = (
        db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            func.sum(BattingStat.runs).label("total_runs"),
            func.sum(BattingStat.balls).label("total_balls")
        )
        .join(BattingStat, Player.id == BattingStat.player_id)
        .join(Inning, BattingStat.inning_id == Inning.id)
        .join(Match, Inning.match_id == Match.id)
        .filter(Match.season == season)
        .group_by(Player.id, Player.name)
        .order_by(func.sum(BattingStat.runs).desc())
        .limit(top_n)
        .all()
    )
    results = []
    for row in leaderboard:
        strike_rate = (row.total_runs / row.total_balls * 100) if row.total_balls > 0 else 0
        results.append(
            schemas.PlayerSeasonStats(
                player_id=row.player_id,
                player_name=row.player_name,
                total_runs=row.total_runs,
                total_balls=row.total_balls,
                strike_rate=round(strike_rate, 2)
            )
        )
    return results

@app.get("/matches/{match_id}", response_model=schemas.MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = (
        db.query(Match)
        .options(
            joinedload(Match.team1),
            joinedload(Match.team2),
            joinedload(Match.innings).joinedload(Inning.team),
            joinedload(Match.innings).joinedload(Inning.batting_stats).joinedload(BattingStat.player),
        )
        .filter(Match.id == match_id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.get("/players/{player_id}/stats", response_model=schemas.PlayerCareerStats, tags=["Players"])
def get_player_career_stats(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    stats = (
        db.query(
            func.count(func.distinct(Inning.match_id)).label("matches_played"),
            func.sum(BattingStat.runs).label("total_runs"),
            func.sum(BattingStat.balls).label("total_balls"),
            func.sum(case((BattingStat.runs >= 50, 1), else_=0)).label("fifties"),
            func.sum(case((BattingStat.runs >= 100, 1), else_=0)).label("hundreds")
        )
        .join(Inning, BattingStat.inning_id == Inning.id)
        .filter(BattingStat.player_id == player_id)
        .first()
    )
    if not stats or stats.total_runs is None:
        return schemas.PlayerCareerStats(
            player_id=player.id, player_name=player.name, matches_played=0,
            total_runs=0, total_balls=0, fifties=0, hundreds=0, strike_rate=0.0
        )
    strike_rate = (stats.total_runs / stats.total_balls * 100) if stats.total_balls > 0 else 0
    return schemas.PlayerCareerStats(
        player_id=player.id,
        player_name=player.name,
        matches_played=stats.matches_played,
        total_runs=stats.total_runs,
        total_balls=stats.total_balls,
        fifties=stats.fifties,
        hundreds=stats.hundreds,
        strike_rate=round(strike_rate, 2)
    )

@app.get("/stats/head-to-head", response_model=schemas.HeadToHeadStats, tags=["Stats"])
def get_head_to_head_stats(team1_id: int, team2_id: int, db: Session = Depends(get_db)):
    team1 = db.query(Team).filter(Team.id == team1_id).first()
    team2 = db.query(Team).filter(Team.id == team2_id).first()
    if not team1 or not team2:
        raise HTTPException(status_code=404, detail="One or both teams not found")
    if team1_id == team2_id:
        raise HTTPException(status_code=400, detail="Team IDs must be different")
    query = db.query(Match).filter(
        ((Match.team1_id == team1_id) & (Match.team2_id == team2_id)) |
        ((Match.team1_id == team2_id) & (Match.team2_id == team1_id))
    )
    total_matches = query.count()
    team1_wins = query.filter(Match.winner_id == team1_id).count()
    team2_wins = query.filter(Match.winner_id == team2_id).count()
    return schemas.HeadToHeadStats(
        team1_name=team1.name,
        team2_name=team2.name,
        total_matches=total_matches,
        team1_wins=team1_wins,
        team2_wins=team2_wins,
    )

@app.get("/players/{player_id}/matches/{match_id}/stats", response_model=schemas.PlayerMatchStats, tags=["Players"])
def get_player_match_stats(player_id: int, match_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    stats = (
        db.query(BattingStat)
        .join(Inning, BattingStat.inning_id == Inning.id)
        .filter(BattingStat.player_id == player_id, Inning.match_id == match_id)
        .first()
    )
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found for this player in this match.")
    strike_rate = (stats.runs / stats.balls * 100) if stats.balls > 0 else 0
    return schemas.PlayerMatchStats(
        player_id=player_id,
        player_name=player.name,
        match_id=match_id,
        runs=stats.runs,
        balls_faced=stats.balls,
        strike_rate=round(strike_rate, 2)
    )

@app.get("/players/search", response_model=List[schemas.PlayerResponse], tags=["Players"])
def search_players(name: str, db: Session = Depends(get_db)):
    if not name or len(name) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters.")
    players = (
        db.query(Player)
        .filter(Player.name.ilike(f"%{name}%"))
        .limit(10)  # Limit to 10 results for performance
        .all()
    )
    if not players:
        raise HTTPException(status_code=404, detail="No players found with that name.")
    return players

@app.get("/players/{player_id}/matches", response_model=List[int], tags=["Players"])
def get_player_matches(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    match_ids = (
        db.query(Inning.match_id)
        .join(BattingStat, BattingStat.inning_id == Inning.id)
        .filter(BattingStat.player_id == player_id)
        .distinct()
        .all()
    )
    return [match_id for (match_id,) in match_ids]

# --- NEW ENDPOINTS FOR DYNAMIC FRONTEND ---

@app.get("/seasons", response_model=List[int], tags=["Frontend Data"])
def get_all_seasons(db: Session = Depends(get_db)):
    """Returns a list of all unique seasons (years) available."""
    seasons = db.query(Match.season).distinct().order_by(Match.season.desc()).all()
    return [s[0] for s in seasons]

@app.get("/matches/season/{season}", response_model=List[schemas.MatchInfo], tags=["Frontend Data"])
def get_matches_by_season(season: int, db: Session = Depends(get_db)):
    """Returns a list of all matches in a season with a user-friendly display title."""
    matches_from_db = (
        db.query(Match)
        .options(joinedload(Match.team1), joinedload(Match.team2))
        .filter(Match.season == season)
        .order_by(Match.date)
        .all()
    )
    if not matches_from_db:
        raise HTTPException(status_code=404, detail="No matches found for this season.")

    response_matches = []
    for match in matches_from_db:
        # --- THIS IS THE FIX ---
        # Add a check to ensure both team objects exist before processing.
        # This handles bad data in the database gracefully.
        if match.team1 and match.team2:
            title = f"{match.team1.name} vs {match.team2.name}"
            if match.date:
                title += f" ({match.date.strftime('%b %d, %Y')})"
            response_matches.append(schemas.MatchInfo(id=match.id, display_title=title))
        else:
            # Optionally, print a warning to the console to identify bad data
            print(f"Skipping Match ID {match.id} due to missing team data.")
    
    return response_matches

@app.get("/matches/{match_id}/players", response_model=Dict[str, List[schemas.PlayerResponse]], tags=["Frontend Data"])
def get_players_in_match(match_id: int, db: Session = Depends(get_db)):
    """Returns a dictionary of teams and players who batted in a specific match."""
    match = db.query(Match).options(joinedload(Match.team1), joinedload(Match.team2)).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    players_by_team = {match.team1.name: [], match.team2.name: []}
    
    batting_stats = (
        db.query(BattingStat)
        .join(Inning)  # No need to specify condition if relationships are set up
        .filter(Inning.match_id == match_id)
        .options(
            # Corrected path: from BattingStat -> Inning -> Team
            joinedload(BattingStat.inning).joinedload(Inning.team),
            joinedload(BattingStat.player)
        )
        .all()
    )

    for stat in batting_stats:
        team_name = stat.inning.team.name
        if team_name in players_by_team and not any(p.id == stat.player.id for p in players_by_team[team_name]):
            players_by_team[team_name].append(stat.player)
    return players_by_team