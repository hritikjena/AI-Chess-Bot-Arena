import math
import random
from sqlalchemy.orm import Session
from Server import models

def generate_knockout_bracket(tournament_id: int, db: Session):
    participants = db.query(models.TournamentParticipant).filter(
        models.TournamentParticipant.tournament_id == tournament_id
    ).all()
    
    num_bots = len(participants)
    if num_bots < 2:
        return False
        
    # Shuffle or seed
    random.shuffle(participants)
    for i, p in enumerate(participants):
        p.seed = i + 1
    
    # Calculate power of 2 bracket size
    bracket_size = 2 ** math.ceil(math.log2(num_bots))
    num_byes = bracket_size - num_bots
    
    # We will build the bracket from the Final backwards to the First Round.
    # Total matches = bracket_size - 1
    # Let's create all empty matches first.
    
    matches_by_round = {}
    current_round_size = 1
    round_idx = 1
    
    # Create the matches (starting from the final)
    while current_round_size <= bracket_size // 2:
        round_name = "Final" if current_round_size == 1 else "Semifinals" if current_round_size == 2 else "Quarterfinals" if current_round_size == 4 else f"Round of {current_round_size * 2}"
        matches_by_round[round_idx] = []
        for i in range(current_round_size):
            m = models.Match(
                tournament_id=tournament_id,
                round_name=round_name,
                match_sequence=i,
                status="PENDING"
            )
            db.add(m)
            matches_by_round[round_idx].append(m)
        current_round_size *= 2
        round_idx += 1
        
    db.commit() # Get IDs
    
    # Link next_match_id (child to parent)
    for r in range(2, round_idx):
        parent_round = matches_by_round[r-1]
        child_round = matches_by_round[r]
        for i, child_match in enumerate(child_round):
            parent_match = parent_round[i // 2]
            child_match.next_match_id = parent_match.id
            
    db.commit()
    
    # Fill the first round (largest round_idx - 1)
    first_round_matches = matches_by_round[round_idx - 1]
    
    # Assign bots to first round slots
    slots = []
    for m in first_round_matches:
        slots.append({"match": m, "bots": []})
        
    # Simple distribution (this can be improved for strict seeded brackets)
    for i, p in enumerate(participants):
        slots[i % len(slots)]["bots"].append(p)
        
    # Apply byes and set PENDING matches
    for slot in slots:
        match = slot["match"]
        bots = slot["bots"]
        if len(bots) == 2:
            match.bot1_id = bots[0].bot_id
            match.bot2_id = bots[1].bot_id
        elif len(bots) == 1:
            # Bye! Automatically advance this bot to the next match
            match.bot1_id = bots[0].bot_id
            match.winner_id = bots[0].bot_id
            match.status = "COMPLETED"
            match.result = "BYE"
            
            # Push to next match
            if match.next_match_id:
                next_m = db.query(models.Match).filter(models.Match.id == match.next_match_id).first()
                if not next_m.bot1_id:
                    next_m.bot1_id = bots[0].bot_id
                else:
                    next_m.bot2_id = bots[0].bot_id
                    
    # Update tournament status
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    tournament.status = "RUNNING"
    db.commit()
    return True

