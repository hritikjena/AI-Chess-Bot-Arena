import chess
import chess.engine
import multiprocessing
import sys
import os
from Engine.CommentaryManager import get_commentary

# Authoritative piece values
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def worker(bot_name, fen, queue):
    # Strip .py extension if present for import
    if bot_name.endswith('.py'):
        bot_name = bot_name[:-3]
        
    # Ensure bots directory is in sys.path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bots_dir = os.path.join(project_root, "bots")
    participant_bots_dir = os.path.join(project_root, "participant_bots")
    
    if bots_dir not in sys.path:
        sys.path.insert(0, bots_dir)
    if participant_bots_dir not in sys.path:
        sys.path.insert(0, participant_bots_dir)

    try:
        module = __import__(bot_name)
        move = module.next_move(fen)
        queue.put(move)
    except Exception as e:
        queue.put(f"ERROR: {str(e)}")

def get_safe_move(bot_name, fen, timeout=4):
    ctx = multiprocessing.get_context("fork")
    queue = ctx.Queue()
    p = ctx.Process(target=worker, args=(bot_name, fen, queue))

    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return None, "timeout"

    if not queue.empty():
        result = queue.get()
        if isinstance(result, str) and result.startswith("ERROR:"):
            return None, result
        return result, None

    return None, "unknown_error"

def get_captured_points(board: chess.Board):
    white_remaining = 0
    black_remaining = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = PIECE_VALUES.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                white_remaining += val
            else:
                black_remaining += val
                
    white_captured_pts = max(0, 39 - black_remaining)
    black_captured_pts = max(0, 39 - white_remaining)
    return white_captured_pts, black_captured_pts

def get_engine_analysis(engine, board):
    if not engine:
        return {"score": 0, "best_move": None, "pv": None}
    try:
        info = engine.analyse(board, chess.engine.Limit(time=0.01))
        # Get score from white's perspective, 10000 = mate
        score = info["score"].white().score(mate_score=10000)
        pv = info.get("pv", [])
        best_move = pv[0].uci() if pv else None
        try:
            pv_str = board.variation_san(pv) if pv else None
        except:
            pv_str = " ".join([m.uci() for m in pv]) if pv else None
        return {"score": score, "best_move": best_move, "pv": pv_str}
    except Exception:
        return {"score": 0, "best_move": None, "pv": None}

def run_match_generator(bot1_name, bot2_name, max_moves=200):
    board = chess.Board()
    move_count = 0
    turn = 0
    
    white_pts, black_pts = get_captured_points(board)
    
    try:
        stockfish_path = os.getenv("STOCKFISH_PATH", "/opt/homebrew/bin/stockfish")
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    except Exception:
        engine = None
        
    prev_analysis = get_engine_analysis(engine, board)

    blunders = {0: 0, 1: 0} # 0=White, 1=Black
    mistakes = {0: 0, 1: 0}
    eval_losses = {0: [], 1: []}
    insights = []

    yield {
        "status": "playing",
        "fen": board.fen(),
        "white_points": white_pts,
        "black_points": black_pts,
        "last_move": None,
        "move_number": move_count,
        "error": None,
        "commentary": None
    }

    while not board.is_game_over() and move_count < max_moves:
        fen = board.fen()
        current_bot = bot1_name if turn == 0 else bot2_name
        
        move, error = get_safe_move(current_bot, fen)
        
        if error:
            yield {
                "status": "error",
                "fen": board.fen(),
                "white_points": white_pts,
                "black_points": black_pts,
                "last_move": None,
                "move_number": move_count,
                "error": f"{current_bot} failed: {error}"
            }
            return

        try:
            move_obj = chess.Move.from_uci(move)
        except Exception:
            yield {
                "status": "error",
                "fen": board.fen(),
                "white_points": white_pts,
                "black_points": black_pts,
                "last_move": move,
                "move_number": move_count,
                "error": f"{current_bot} gave invalid format: {move}"
            }
            return

        if move_obj not in board.legal_moves:
            yield {
                "status": "error",
                "fen": board.fen(),
                "white_points": white_pts,
                "black_points": black_pts,
                "last_move": move,
                "move_number": move_count,
                "error": f"{current_bot} played illegal move: {move}"
            }
            return

        san_move = board.san(move_obj)
        board.push(move_obj)
        move_count += 1
        
        just_played = turn
        turn = 1 - turn
        
        white_pts, black_pts = get_captured_points(board)
        new_analysis = get_engine_analysis(engine, board)
        
        commentary = None
        
        if engine and prev_analysis["score"] is not None and new_analysis["score"] is not None:
            # Score is from white's perspective
            prev_s = prev_analysis["score"] / 100.0
            new_s = new_analysis["score"] / 100.0
            
            if just_played == 0: # White
                loss = prev_s - new_s
            else: # Black
                loss = new_s - prev_s
                
            if loss > 0:
                eval_losses[just_played].append(loss)
                if loss >= 1.5:
                    blunders[just_played] += 1
                elif loss >= 0.7:
                    mistakes[just_played] += 1

            commentary = get_commentary(
                board_fen=board.fen(),
                move_san=san_move,
                prev_analysis=prev_analysis,
                new_analysis=new_analysis
            )
            
            if commentary and not commentary.startswith("[Error]"):
                insights.append({
                    "move_number": move_count,
                    "color": "white" if just_played == 0 else "black",
                    "move": san_move,
                    "eval_before": prev_s,
                    "eval_after": new_s,
                    "loss": loss,
                    "commentary": commentary,
                    "fen": board.fen()
                })
            
        prev_analysis = new_analysis
        
        status = "playing"
        if board.is_game_over() or move_count >= max_moves:
            status = "finished"

        yield {
            "status": status,
            "fen": board.fen(),
            "white_points": white_pts,
            "black_points": black_pts,
            "last_move": san_move,
            "move_number": move_count,
            "error": None,
            "commentary": commentary
        }

    # Yield final result if finished normally
    result_str = board.result()
    reason = "Unknown"
    if board.is_checkmate():
        reason = "Checkmate"
    elif board.is_stalemate():
        reason = "Stalemate"
    elif board.is_insufficient_material():
        reason = "Insufficient Material"
    elif board.can_claim_threefold_repetition():
        reason = "Threefold Repetition"
    elif board.can_claim_fifty_moves():
        reason = "50-Move Rule"
    elif move_count >= max_moves:
        reason = "Move Limit Reached"
        result_str = "1/2-1/2"

    if engine:
        engine.quit()
        
    avg_loss_w = sum(eval_losses[0])/len(eval_losses[0]) if eval_losses[0] else 0.0
    avg_loss_b = sum(eval_losses[1])/len(eval_losses[1]) if eval_losses[1] else 0.0
    
    analysis_summary = {
        "bot1": {
            "blunders": blunders[0],
            "mistakes": mistakes[0],
            "avg_eval_loss": avg_loss_w
        },
        "bot2": {
            "blunders": blunders[1],
            "mistakes": mistakes[1],
            "avg_eval_loss": avg_loss_b
        }
    }

    yield {
        "status": "completed",
        "result": result_str,
        "reason": reason,
        "fen": board.fen(),
        "commentary": None,
        "analysis_summary": analysis_summary,
        "insights": insights
    }
