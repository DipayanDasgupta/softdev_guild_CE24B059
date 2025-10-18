from sqlalchemy.orm import Session
from db import SessionLocal
from models import Player, Team, Match, Inning, BattingStat

def insert_test_data():
    db = SessionLocal()
    try:
        # Insert teams
        team1 = db.query(Team).filter_by(id=1).first()
        if not team1:
            team1 = Team(id=1, name='Kolkata Knight Riders')
            db.add(team1)
        team2 = db.query(Team).filter_by(id=2).first()
        if not team2:
            team2 = Team(id=2, name='Royal Challengers Bangalore')
            db.add(team2)
        
        # Insert player
        player = db.query(Player).filter_by(id=2).first()
        if not player:
            player = Player(id=2, name='Brendon McCullum')
            db.add(player)
        
        # Insert match
        match = db.query(Match).filter_by(id=1).first()
        if not match:
            match = Match(id=1, season=2023, team1_id=1, team2_id=2)
            db.add(match)
        
        # Insert inning
        inning = db.query(Inning).filter_by(id=1).first()
        if not inning:
            inning = Inning(id=1, match_id=1, team_id=1, innings_no=1)
            db.add(inning)
        
        # Insert batting stats
        stat = db.query(BattingStat).filter_by(inning_id=1, player_id=2).first()
        if not stat:
            stat = BattingStat(inning_id=1, player_id=2, runs=50, balls=30, fours=5, sixes=2, strike_rate=166.67)
            db.add(stat)
        
        db.commit()
        print("Test data inserted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting test data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()