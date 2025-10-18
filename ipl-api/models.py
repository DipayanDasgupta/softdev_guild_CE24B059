from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from db import Base

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    batting_stats = relationship("BattingStat", back_populates="player")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    matches_team1 = relationship("Match", back_populates="team1", foreign_keys="Match.team1_id")
    matches_team2 = relationship("Match", back_populates="team2", foreign_keys="Match.team2_id")
    innings = relationship("Inning", back_populates="team")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)
    venue = Column(String, nullable=True)
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="matches_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="matches_team2")
    innings = relationship("Inning", back_populates="match")

class Inning(Base):
    __tablename__ = "innings"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    innings_no = Column(Integer, nullable=False)
    match = relationship("Match", back_populates="innings")
    team = relationship("Team", back_populates="innings")
    batting_stats = relationship("BattingStat", back_populates="inning")

class BattingStat(Base):
    __tablename__ = "batting_stats"
    id = Column(Integer, primary_key=True, index=True)
    inning_id = Column(Integer, ForeignKey("innings.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    runs = Column(Integer, nullable=False)
    balls = Column(Integer, nullable=False)
    fours = Column(Integer, nullable=False)
    sixes = Column(Integer, nullable=False)
    strike_rate = Column(Float, nullable=True)
    inning = relationship("Inning", back_populates="batting_stats")
    player = relationship("Player", back_populates="batting_stats")