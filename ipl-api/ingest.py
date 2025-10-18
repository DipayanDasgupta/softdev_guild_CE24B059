import json
import re
from sqlalchemy.orm import Session
from db import Base, engine, SessionLocal
from models import Player, Team, Match, Inning, BattingStat
from schemas import MatchSchema

def create_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

def get_or_create(session: Session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance

def clean_player_name(name: str) -> str:
    return re.sub(r'\s*\(c\)\s*|\s*†\s*|\s*\*+\s*$', '', name).strip()

def safe_int(val: str) -> int:
    return int(val) if val and val.isdigit() else 0

def safe_float(val: str):
    if val in ("-", "", None):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def ingest_match_data(session: Session, match_data: dict, season: int):
    try:
        if 'teams' not in match_data or 'innings' not in match_data:
            print(f"Skipping a match in season {season}: Missing 'teams' or 'innings' key.")
            return
        info_dict = {
            "teams": match_data["teams"],
            "dates": None,
            "venue": None,
            "outcome": None
        }
        cleaned_data = {
            "info": info_dict,
            "innings": match_data.get("innings", [])
        }
        match_info = MatchSchema(**cleaned_data)
        info = match_info.info
        team1 = get_or_create(session, Team, name=info.teams[0])
        team2 = get_or_create(session, Team, name=info.teams[1])
        match = Match(
            season=season,
            date=None,
            venue=None,
            team1_id=team1.id,
            team2_id=team2.id,
            winner_id=None
        )
        session.add(match)
        session.flush()
        for idx, inn_data in enumerate(match_info.innings, start=1):
            batting_team_short_name = info.teams[idx-1]
            batting_team = get_or_create(session, Team, name=batting_team_short_name)
            inning = Inning(
                match_id=match.id,
                team_id=batting_team.id,
                innings_no=idx
            )
            session.add(inning)
            session.flush()
            for b_stat in inn_data.batting:
                if "player" not in b_stat:
                    continue
                cleaned_name = clean_player_name(b_stat["player"])
                player = get_or_create(session, Player, name=cleaned_name)
                stat = BattingStat(
                    inning_id=inning.id,
                    player_id=player.id,
                    runs=safe_int(b_stat.get("runs")),
                    balls=safe_int(b_stat.get("balls")),
                    fours=safe_int(b_stat.get("fours")),
                    sixes=safe_int(b_stat.get("sixes")),
                    strike_rate=safe_float(b_stat.get("strike_rate")),
                )
                session.add(stat)
        session.commit()
        print(f"Successfully ingested match: {info.teams[0]} vs {info.teams[1]}")
    except Exception as e:
        session.rollback()
        print(f"Failed to ingest a match for season {season}. Error: {e}")

if __name__ == "__main__":
    create_database()
    db = SessionLocal()
    for year in range(2008, 2025):
        file_path = f"ipl_{year}.json"
        print(f"\n--- Processing Season {year} ---")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                matches_in_season = json.load(f)
            for match_json in matches_in_season:
                ingest_match_data(db, match_json, season=year)
        except FileNotFoundError:
            print(f"Data file not found for season {year}: {file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {file_path}: {e}")
    db.close()
    print("\n--- Data ingestion complete for all seasons. ---")