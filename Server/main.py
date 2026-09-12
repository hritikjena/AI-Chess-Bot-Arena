from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from . import models, schemas
from .database import engine, get_db
import sys
import os
import asyncio

# Ensure parent directory is in path for Engine imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.MatchManager import run_match_generator

models.Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from Engine.Orchestrator import orchestrator_loop
    # Start the orchestrator as a background task
    task = asyncio.create_task(orchestrator_loop())
    yield
    task.cancel()

app = FastAPI(title="Chess Bot Arena API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Chess Bot Arena API"}

@app.post("/api/bots/", response_model=schemas.BotResponse)
def create_bot(bot: schemas.BotCreate, db: Session = Depends(get_db)):
    db_bot = models.Bot(name=bot.name, filename=bot.filename, description=bot.description)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@app.get("/api/bots/", response_model=list[schemas.BotResponse])
def read_bots(db: Session = Depends(get_db)):
    bots = db.query(models.Bot).all()
    return bots

@app.post("/api/matches/", response_model=schemas.MatchResponse)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    bot1 = db.query(models.Bot).filter(models.Bot.id == match.bot1_id).first()
    bot2 = db.query(models.Bot).filter(models.Bot.id == match.bot2_id).first()
    
    if not bot1 or not bot2:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    db_match = models.Match(bot1_id=bot1.id, bot2_id=bot2.id)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

@app.get("/api/matches/{match_id}", response_model=schemas.MatchResponse)
def read_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.post("/api/tournaments/", response_model=schemas.TournamentResponse)
def create_tournament(tournament: schemas.TournamentCreate, db: Session = Depends(get_db)):
    db_tournament = models.Tournament(
        name=tournament.name, 
        description=tournament.description,
        format=tournament.format,
        participant_limit=tournament.participant_limit,
        registration_start=tournament.registration_start,
        registration_end=tournament.registration_end,
        tournament_start=tournament.tournament_start,
        tournament_end=tournament.tournament_end,
        status="DRAFT" if tournament.registration_start else "REGISTRATION_OPEN"
    )
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

@app.get("/api/tournaments/", response_model=list[schemas.TournamentResponse])
def read_tournaments(db: Session = Depends(get_db)):
    return db.query(models.Tournament).all()

@app.get("/api/tournaments/{tournament_id}", response_model=schemas.TournamentResponse)
def read_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament

@app.post("/api/tournaments/{tournament_id}/register", response_model=schemas.TournamentParticipantResponse)
def register_for_tournament(tournament_id: int, bot_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
        
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    # Check limit
    current_count = db.query(models.TournamentParticipant).filter(models.TournamentParticipant.tournament_id == tournament_id).count()
    if current_count >= tournament.participant_limit:
        raise HTTPException(status_code=400, detail="Tournament is full")
        
    # Check if already registered
    existing = db.query(models.TournamentParticipant).filter(
        models.TournamentParticipant.tournament_id == tournament_id,
        models.TournamentParticipant.bot_id == bot_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bot already registered")
        
    participant = models.TournamentParticipant(tournament_id=tournament_id, bot_id=bot_id)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant

@app.post("/api/tournaments/{tournament_id}/start")
def start_tournament(tournament_id: int, db: Session = Depends(get_db)):
    from Engine.TournamentManager import generate_knockout_bracket
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
        
    if tournament.status != "REGISTRATION_OPEN":
        raise HTTPException(status_code=400, detail="Tournament cannot be started")
        
    success = generate_knockout_bracket(tournament_id, db)
    if not success:
        raise HTTPException(status_code=400, detail="Not enough participants")
        
    return {"message": "Tournament started successfully"}

@app.get("/api/tournaments/{tournament_id}/participants", response_model=list[schemas.TournamentParticipantResponse])
def read_tournament_participants(tournament_id: int, db: Session = Depends(get_db)):
    return db.query(models.TournamentParticipant).filter(models.TournamentParticipant.tournament_id == tournament_id).all()

@app.get("/api/tournaments/{tournament_id}/matches", response_model=list[schemas.MatchResponse])
def read_tournament_matches(tournament_id: int, db: Session = Depends(get_db)):
    return db.query(models.Match).filter(models.Match.tournament_id == tournament_id).all()

@app.websocket("/api/ws/match/{match_id}")
async def websocket_match(websocket: WebSocket, match_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        await websocket.send_json({"error": "Match not found"})
        await websocket.close()
        return
        
    bot1 = db.query(models.Bot).filter(models.Bot.id == match.bot1_id).first()
    bot2 = db.query(models.Bot).filter(models.Bot.id == match.bot2_id).first()
    
    if not bot1 or not bot2:
        await websocket.send_json({"error": "Bots not found for this match"})
        await websocket.close()
        return

    moves = []
    final_fen = ""
    result = None
    reason = None
    
    # Run the match generator synchronously but yield to event loop
    generator = run_match_generator(bot1.filename, bot2.filename)
    
    try:
        for state in generator:
            if state["status"] == "completed":
                result = state.get("result")
                reason = state.get("reason")
                final_fen = state.get("fen")
                await websocket.send_json(state)
                break
                
            if state["last_move"]:
                moves.append(state["last_move"])
                
            await websocket.send_json(state)
            await asyncio.sleep(0.5) # Add a small delay for visualization
            
    except WebSocketDisconnect:
        print(f"Client disconnected from match {match_id}")
    finally:
        # Save match results
        match.moves = moves
        match.final_fen = final_fen
        match.result = result
        match.reason = reason
        db.commit()
        try:
            if not websocket.client_state.name == "DISCONNECTED":
                await websocket.close()
        except Exception:
            pass

last_gemini_summary = None
last_gemini_stats_hash = None

@app.get("/api/analytics/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    global last_gemini_summary, last_gemini_stats_hash
    
    total_bots = db.query(models.Bot).count()
    total_games = db.query(models.Match).filter(models.Match.status == "COMPLETED").count()
    total_tournaments = db.query(models.Tournament).count()
    active_tournaments = db.query(models.Tournament).filter(models.Tournament.status.in_(["RUNNING", "REGISTRATION_OPEN"])).count()
    
    summary = schemas.AnalyticsSummary(
        total_bots=total_bots,
        total_games=total_games,
        total_tournaments=total_tournaments,
        active_tournaments=active_tournaments
    )
    
    bots = db.query(models.Bot).all()
    bot_performance = []
    
    for bot in bots:
        bot_matches = db.query(models.Match).filter(
            (models.Match.bot1_id == bot.id) | (models.Match.bot2_id == bot.id),
            models.Match.status == "COMPLETED"
        ).all()
        
        games_played = len(bot_matches)
        wins = 0
        losses = 0
        draws = 0
        blunders = 0
        mistakes = 0
        eval_losses = []
        
        for m in bot_matches:
            if m.winner_id == bot.id:
                wins += 1
            elif m.result == "1/2-1/2" or m.winner_id is None:
                draws += 1
            else:
                losses += 1
                
            if m.analysis_summary:
                key = "bot1" if m.bot1_id == bot.id else "bot2"
                stats = m.analysis_summary.get(key, {})
                blunders += stats.get("blunders", 0)
                mistakes += stats.get("mistakes", 0)
                eval_losses.append(stats.get("avg_eval_loss", 0.0))
                
        avg_eval_loss = sum(eval_losses)/len(eval_losses) if eval_losses else 0.0
        win_rate = (wins / games_played) * 100 if games_played > 0 else 0.0
        
        bot_performance.append(schemas.BotPerformance(
            bot_id=bot.id,
            bot_name=bot.name,
            games_played=games_played,
            wins=wins,
            losses=losses,
            draws=draws,
            win_rate=win_rate,
            avg_eval_loss=avg_eval_loss,
            total_blunders=blunders,
            total_mistakes=mistakes
        ))
        
    recent_games = db.query(models.Match).filter(models.Match.status == "COMPLETED").order_by(models.Match.id.desc()).limit(5).all()
    live_games = db.query(models.Match).filter(models.Match.status == "RUNNING").limit(5).all()
    
    all_insights = []
    insight_matches = db.query(models.Match).filter(models.Match.insights != None).order_by(models.Match.id.desc()).limit(10).all()
    for im in insight_matches:
        if im.insights:
            for item in im.insights:
                item["match_id"] = im.id
                all_insights.append(item)
    
    grandmaster_summary = "Not enough data yet. Run some tournaments to get AI insights!"
    if total_games > 0:
        import hashlib
        import json
        from google import genai
        
        top_bots = sorted(bot_performance, key=lambda x: x.win_rate, reverse=True)[:3]
        stats_dict = {
            "total_games": total_games,
            "top_bots": [{"name": b.bot_name, "win_rate": b.win_rate} for b in top_bots]
        }
        
        stats_str = json.dumps(stats_dict, sort_keys=True)
        stats_hash = hashlib.md5(stats_str.encode()).hexdigest()
        
        if stats_hash == last_gemini_stats_hash and last_gemini_summary:
            grandmaster_summary = last_gemini_summary
        else:
            try:
                model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
                client = genai.Client()
                prompt = f"You are a Grandmaster AI summarizing a Chess Bot Arena. Here are the current stats: {stats_str}. Provide a 2-3 sentence enthusiastic summary of the arena's health and who the top contenders are."
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                grandmaster_summary = response.text
                last_gemini_summary = grandmaster_summary
                last_gemini_stats_hash = stats_hash
            except Exception as e:
                grandmaster_summary = f"Arena is thriving with {total_games} games played! (AI temporarily unavailable)"

    return schemas.DashboardResponse(
        summary=summary,
        bot_performance=bot_performance,
        recent_games=recent_games,
        live_games=live_games,
        ai_insights=all_insights[:20],
        grandmaster_summary=grandmaster_summary
    )
