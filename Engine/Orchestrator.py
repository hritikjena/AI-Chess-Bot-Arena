import asyncio
import sys
import os
from sqlalchemy.orm import Session
from Server import models
from Server.database import SessionLocal
from Engine.MatchManager import run_match_generator

async def process_match(match_id: int):
    """
    Run a single match by calling the generator asynchronously.
    """
    db: Session = SessionLocal()
    try:
        match = db.query(models.Match).filter(models.Match.id == match_id).first()
        if not match or match.status != "QUEUED":
            return
            
        bot1 = db.query(models.Bot).filter(models.Bot.id == match.bot1_id).first()
        bot2 = db.query(models.Bot).filter(models.Bot.id == match.bot2_id).first()
        
        if not bot1 or not bot2:
            match.status = "FAILED"
            match.reason = "Bots missing"
            db.commit()
            return
            
        match.status = "RUNNING"
        db.commit()
        
        moves = []
        final_fen = ""
        result = None
        reason = None
        
        # We use asyncio.to_thread to run the generator loop so it doesn't block
        # the main asyncio event loop. But since it yields, we actually just
        # run the whole generator locally.
        def run_match():
            gen = run_match_generator(bot1.filename, bot2.filename)
            last_state = None
            ms = []
            for state in gen:
                if state["last_move"]:
                    ms.append(state["last_move"])
                last_state = state
            return ms, last_state

        ms, last_state = await asyncio.to_thread(run_match)
        
        if last_state and last_state["status"] == "completed":
            result = last_state.get("result")
            reason = last_state.get("reason")
            final_fen = last_state.get("fen")
            analysis_summary = last_state.get("analysis_summary")
            insights = last_state.get("insights")
        else:
            result = "Error"
            reason = "Generator failed"
            analysis_summary = None
            insights = None
            
        # Parse result to find winner
        winner_id = None
        if result == "1-0":
            winner_id = bot1.id
        elif result == "0-1":
            winner_id = bot2.id
            
        # Update match
        match.status = "COMPLETED"
        match.result = result
        match.reason = reason
        match.moves = ms
        match.final_fen = final_fen
        match.winner_id = winner_id
        match.analysis_summary = analysis_summary
        match.insights = insights
        db.commit()
        
        # Advance winner
        if match.tournament_id:
            loser_id = bot1.id if winner_id == bot2.id else bot2.id
            if loser_id:
                loser_participant = db.query(models.TournamentParticipant).filter(
                    models.TournamentParticipant.tournament_id == match.tournament_id,
                    models.TournamentParticipant.bot_id == loser_id
                ).first()
                if loser_participant:
                    loser_participant.status = "ELIMINATED"
            
            if winner_id and match.next_match_id:
                next_m = db.query(models.Match).filter(models.Match.id == match.next_match_id).first()
                if not next_m.bot1_id:
                    next_m.bot1_id = winner_id
                else:
                    next_m.bot2_id = winner_id
            elif winner_id and not match.next_match_id:
                # Tournament finished!
                tournament = db.query(models.Tournament).filter(models.Tournament.id == match.tournament_id).first()
                if tournament:
                    tournament.status = "COMPLETED"
                
                winner_participant = db.query(models.TournamentParticipant).filter(
                    models.TournamentParticipant.tournament_id == match.tournament_id,
                    models.TournamentParticipant.bot_id == winner_id
                ).first()
                if winner_participant:
                    winner_participant.status = "CHAMPION"
            db.commit()
        else:
            if winner_id and match.next_match_id:
                next_m = db.query(models.Match).filter(models.Match.id == match.next_match_id).first()
                if not next_m.bot1_id:
                    next_m.bot1_id = winner_id
                else:
                    next_m.bot2_id = winner_id
                db.commit()
            
    except Exception as e:
        print(f"Error processing match {match_id}: {e}")
        match.status = "FAILED"
        match.reason = str(e)
        db.commit()
    finally:
        db.close()


async def orchestrator_loop():
    """
    Continuously poll the database for PENDING matches that are ready.
    """
    print("Started Orchestrator Loop")
    while True:
        try:
            db: Session = SessionLocal()
            
            # Find a match that is PENDING and has both bots
            match = db.query(models.Match).filter(
                models.Match.status == "PENDING",
                models.Match.bot1_id != None,
                models.Match.bot2_id != None
            ).first()
            
            if match:
                print(f"Orchestrator: Queuing Match {match.id}")
                match.status = "QUEUED"
                db.commit()
                # Fire and forget processing
                asyncio.create_task(process_match(match.id))
            
            db.close()
            await asyncio.sleep(2) # Poll interval
        except Exception as e:
            print(f"Orchestrator error: {e}")
            await asyncio.sleep(5)
