from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BotBase(BaseModel):
    name: str
    filename: str
    description: Optional[str] = ""

class BotCreate(BotBase):
    pass

class BotResponse(BotBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TournamentParticipantResponse(BaseModel):
    id: int
    tournament_id: int
    bot_id: int
    seed: Optional[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchCreate(BaseModel):
    bot1_id: Optional[int]
    bot2_id: Optional[int]
    tournament_id: Optional[int] = None
    max_moves: Optional[int] = 200

class MatchResponse(BaseModel):
    id: int
    bot1_id: Optional[int]
    bot2_id: Optional[int]
    winner_id: Optional[int]
    result: Optional[str]
    reason: Optional[str]
    moves: List[str]
    final_fen: Optional[str]
    tournament_id: Optional[int] = None
    
    analysis_summary: Optional[dict] = None
    insights: Optional[List[dict]] = None
    
    round_name: Optional[str]
    match_sequence: Optional[int]
    next_match_id: Optional[int]
    status: str
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    format: str = "KNOCKOUT"
    participant_limit: int = 16
    
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    tournament_start: Optional[datetime] = None
    tournament_end: Optional[datetime] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentResponse(TournamentBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BotPerformance(BaseModel):
    bot_id: int
    bot_name: str
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    avg_eval_loss: float
    total_blunders: int
    total_mistakes: int

class AnalyticsSummary(BaseModel):
    total_bots: int
    total_games: int
    total_tournaments: int
    active_tournaments: int

class DashboardResponse(BaseModel):
    summary: AnalyticsSummary
    bot_performance: List[BotPerformance]
    recent_games: List[MatchResponse]
    live_games: List[MatchResponse]
    ai_insights: List[dict]
    grandmaster_summary: str
