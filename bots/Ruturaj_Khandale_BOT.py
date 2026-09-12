import chess
import random
import time

piece_weights = {
    chess.PAWN: 10,
    chess.KNIGHT: 30,
    chess.BISHOP: 32,
    chess.ROOK: 50,
    chess.QUEEN: 90,
    chess.KING: 900
}

def piece_value(piece_type):
    if not piece_type: 
        return 0
    return piece_weights.get(piece_type, 0)

def eval_board(board):
    if board.is_checkmate():
        return -999999 if board.turn else 999999


    score = random.randint(-2, 2)
   
    queens_on_board = 0
    for sq in chess.SQUARES:
        if board.piece_type_at(sq) == chess.QUEEN:
            queens_on_board += 1
    is_endgame = (queens_on_board == 0)
    
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if not piece: 
            continue
            
        val = piece_weights[piece.piece_type]
        
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)
        dist_from_center = max(abs(file - 3.5), abs(rank - 3.5))
        center_bonus = int((3.5 - dist_from_center) * 2)
        
        if piece.piece_type == chess.KING:
            if not is_endgame:
                val -= center_bonus * 3
            else:
                val += center_bonus * 2
        else:
            val += center_bonus
            
        if is_endgame:
            # We will handle endgame king chasing globally at the end of the function
            pass
        else:
            if piece.color == chess.WHITE:
                val += rank * 1
            else:
                val += (7 - rank) * 1
                
        if piece.color == chess.WHITE:
            score += val
        else:
            score -= val
            
    if is_endgame:
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        if white_king and black_king:
            wk_f, wk_r = chess.square_file(white_king), chess.square_rank(white_king)
            bk_f, bk_r = chess.square_file(black_king), chess.square_rank(black_king)
            
            wk_dist_center = abs(wk_f - 3.5) + abs(wk_r - 3.5)
            bk_dist_center = abs(bk_f - 3.5) + abs(bk_r - 3.5)
            king_dist = abs(wk_f - bk_f) + abs(wk_r - bk_r)
            
            # If White is winning, push Black King to corner and bring White King close
            if score > 20:
                score += int(bk_dist_center * 15)
                score += int((14 - king_dist) * 15)
            # If Black is winning, push White King to corner and bring Black King close
            elif score < -20:
                score -= int(wk_dist_center * 15)
                score -= int((14 - king_dist) * 15)
            
    return score

class TimeoutException(Exception):
    pass

def sort_moves(board):
    moves = list(board.legal_moves)
    def move_val(m):
        score = 0
        
        if board.is_capture(m):
            victim = board.piece_type_at(m.to_square)
            attacker = board.piece_type_at(m.from_square)
            score += 100 * piece_value(victim) - piece_value(attacker)
            
        if board.gives_check(m): 
            score += 50
            
        if m.promotion:
            score += 900
            
        return score
        
    moves.sort(key=move_val, reverse=True)
    return moves

def quiescence(board, alpha, beta, is_white, end_time):
    if time.time() > end_time:
        raise TimeoutException()
        
    stand_pat = eval_board(board)
    
    if is_white:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
            
        for m in sort_moves(board):
            if not board.is_capture(m): continue
            board.push(m)
            try:
                score = quiescence(board, alpha, beta, False, end_time)
            finally:
                board.pop()
                
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat
            
        for m in sort_moves(board):
            if not board.is_capture(m): continue
            board.push(m)
            try:
                score = quiescence(board, alpha, beta, True, end_time)
            finally:
                board.pop()
                
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta

def run_alphabeta(board, depth, alpha, beta, is_white, end_time):
    if time.time() > end_time:
        raise TimeoutException()
        
    moves = sort_moves(board)
    
    # Instant game-over check without using the slow is_game_over() function!
    if not moves:
        if board.is_check():
            return -999999 if board.turn else 999999
        return 0 # Stalemate
        
    if depth == 0:
        return quiescence(board, alpha, beta, is_white, end_time)
    
    if is_white:
        best_val = -999999
        for m in moves:
            board.push(m)
            try:
                val = run_alphabeta(board, depth - 1, alpha, beta, False, end_time)
            finally:
                board.pop()
            
            best_val = max(best_val, val)
            alpha = max(alpha, best_val)
            if beta <= alpha: 
                break 
        return best_val
    else:
        best_val = 999999
        for m in moves:
            board.push(m)
            try:
                val = run_alphabeta(board, depth - 1, alpha, beta, True, end_time)
            finally:
                board.pop()
                
            best_val = min(best_val, val)
            beta = min(beta, best_val)
            if beta <= alpha: 
                break 
        return best_val

def next_move(fen):
    board = chess.Board(fen)
    moves = sort_moves(board)
    
    if not moves:
        return None
        
    best_move = moves[0] 
    is_w = board.turn == chess.WHITE
    
    end_time = time.time() + 2.0
    
    current_depth = 1
    
    while True:
        try:
            alpha = -999999
            beta = 999999
            current_best_score = -999999 if is_w else 999999
            current_best_move = best_move
            
            for m in moves:
                if time.time() > end_time:
                    raise TimeoutException()
                    
                board.push(m)
                try:
                    # Check for draw ONLY at the root level to prevent massive lag!
                    if board.can_claim_threefold_repetition():
                        score = 0
                    else:
                        score = run_alphabeta(board, current_depth - 1, alpha, beta, not is_w, end_time)
                finally:
                    board.pop()
                
                if is_w:
                    if score > current_best_score:
                        current_best_score = score
                        current_best_move = m
                    alpha = max(alpha, current_best_score)
                else:
                    if score < current_best_score:
                        current_best_score = score
                        current_best_move = m
                    beta = min(beta, current_best_score)
            
            best_move = current_best_move
            current_depth += 1
            
            if current_depth > 6:
                break
                
        except TimeoutException:
            break
            
    return str(best_move)
