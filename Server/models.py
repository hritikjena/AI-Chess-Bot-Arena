from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    filename = Column(String)  # The module name, e.g. "bot_greedy"
    description = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    status = Column(String, default="DRAFT") # DRAFT, REGISTRATION_OPEN, REGISTRATION_CLOSED, RUNNING, COMPLETED, CANCELLED
    format = Column(String, default="KNOCKOUT")
    participant_limit = Column(Integer, default=16)
    
    registration_start = Column(DateTime(timezone=True), nullable=True)
    registration_end = Column(DateTime(timezone=True), nullable=True)
    tournament_start = Column(DateTime(timezone=True), nullable=True)
    tournament_end = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    matches = relationship("Match", backref="tournament", cascade="all, delete-orphan")
    participants = relationship("TournamentParticipant", backref="tournament", cascade="all, delete-orphan")

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    bot_id = Column(Integer, ForeignKey("bots.id"))
    seed = Column(Integer, nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, ELIMINATED, CHAMPION
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=True)
    
    # Bracket progression logic
    round_name = Column(String, nullable=True) # e.g. "Quarterfinal", "Round of 16"
    match_sequence = Column(Integer, nullable=True) # order in the round
    next_match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    
    bot1_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    bot2_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    
    status = Column(String, default="PENDING") # PENDING, QUEUED, RUNNING, COMPLETED, FAILED
    
    result = Column(String, nullable=True) # "1-0", "0-1", "1/2-1/2"
    reason = Column(String, nullable=True)
    moves = Column(JSON, default=list) # Store list of UCI strings
    final_fen = Column(String, nullable=True)
    
    # AI Analytics
    analysis_summary = Column(JSON, nullable=True) # { "blunders": 2, "mistakes": 5, "avg_eval_loss": 0.4 }
    insights = Column(JSON, nullable=True) # list of critical moments with commentary
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
