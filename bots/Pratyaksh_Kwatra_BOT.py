import chess
import chess.polyglot
import time
import random

PIECE_VALUES = {
    chess.PAWN: (100, 100),
    chess.KNIGHT: (320, 280),
    chess.BISHOP: (330, 310),
    chess.ROOK: (500, 550),
    chess.QUEEN: (900, 1000),
    chess.KING: (0, 0)
}

PAWN_PST_MG = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

PAWN_PST_EG = [
    0,  0,  0,  0,  0,  0,  0,  0,
    80, 80, 80, 80, 80, 80, 80, 80,
    50, 50, 50, 50, 50, 50, 50, 50,
    30, 30, 30, 30, 30, 30, 30, 30,
    20, 20, 20, 20, 20, 20, 20, 20,
    10, 10, 10, 10, 10, 10, 10, 10,
    10, 10, 10, 10, 10, 10, 10, 10,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_PST_MG = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

KING_PST_EG = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

PST_TABLES = {
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST
}

PHASE_WEIGHTS = {
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4
}
TOTAL_PHASE = 24

transposition_table = {}
killer_moves = [[None, None] for _ in range(100)]
history_table = {}

def get_hash(board):
    return chess.polyglot.zobrist_hash(board)

def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition():
        return 0

    mg_score = 0
    eg_score = 0
    phase = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            p_type = piece.piece_type
            color_mult = 1 if piece.color == chess.WHITE else -1
            
            mg_val, eg_val = PIECE_VALUES[p_type]
            mg_score += mg_val * color_mult
            eg_score += eg_val * color_mult
            
            phase += PHASE_WEIGHTS.get(p_type, 0)
            
            sq = chess.square_mirror(square) if piece.color == chess.WHITE else square
            if p_type == chess.PAWN:
                mg_score += PAWN_PST_MG[sq] * color_mult
                eg_score += PAWN_PST_EG[sq] * color_mult
            elif p_type == chess.KING:
                mg_score += KING_PST_MG[sq] * color_mult
                eg_score += KING_PST_EG[sq] * color_mult
            else:
                pst = PST_TABLES.get(p_type)
                if pst:
                    mg_score += pst[sq] * color_mult
                    eg_score += pst[sq] * color_mult

    phase = min(phase, TOTAL_PHASE)
    mg_phase = phase
    eg_phase = TOTAL_PHASE - phase
    score = (mg_score * mg_phase + eg_score * eg_phase) // TOTAL_PHASE
    
    # Position bonuses
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2: score += 30
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2: score -= 30
    
    return score

def move_priority(board, move, depth, tt_move=None):
    if move == tt_move: return 1000000
    priority = 0
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            priority = 10000 + PIECE_VALUES[victim.piece_type][0] * 10 - PIECE_VALUES[attacker.piece_type][0]
    elif move == killer_moves[depth][0]: priority = 9000
    elif move == killer_moves[depth][1]: priority = 8000
    else: priority = history_table.get((board.turn, move.from_square, move.to_square), 0)
    if move.promotion: priority += 5000
    return priority

def quiescence_search(board, alpha, beta):
    stand_pat = evaluate_board(board)
    if board.turn == chess.BLACK: stand_pat = -stand_pat
    if stand_pat >= beta: return beta
    if alpha < stand_pat: alpha = stand_pat
    moves = [m for m in board.legal_moves if board.is_capture(m)]
    moves.sort(key=lambda m: move_priority(board, m, 0), reverse=True)
    for move in moves:
        board.push(move)
        score = -quiescence_search(board, -beta, -alpha)
        board.pop()
        if score >= beta: return beta
        if score > alpha: alpha = score
    return alpha

def alphabeta(board, depth, alpha, beta, maximizing_player, start_time, time_limit, current_depth):
    if time.time() - start_time > time_limit: raise TimeoutError
    board_hash = get_hash(board)
    tt_entry = transposition_table.get(board_hash)
    tt_move = None
    if tt_entry and tt_entry['depth'] >= depth:
        if tt_entry['type'] == 'exact': return tt_entry['score']
        elif tt_entry['type'] == 'lower' and tt_entry['score'] >= beta: return tt_entry['score']
        elif tt_entry['type'] == 'upper' and tt_entry['score'] <= alpha: return tt_entry['score']
        tt_move = tt_entry['move']
    if depth == 0 or board.is_game_over(): return quiescence_search(board, alpha, beta)
    if depth >= 3 and not board.is_check():
        board.push(chess.Move.null())
        try:
            score = -alphabeta(board, depth - 3, -beta, -beta + 1, not maximizing_player, start_time, time_limit, current_depth + 1)
        except TimeoutError:
            board.pop()
            raise TimeoutError
        board.pop()
        if score >= beta: return beta
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: move_priority(board, m, current_depth, tt_move), reverse=True)
    best_val = -float('inf')
    best_move = None
    original_alpha = alpha
    for i, move in enumerate(moves):
        board.push(move)
        try:
            if depth >= 3 and i >= 4 and not board.is_capture(move) and not board.is_check():
                score = -alphabeta(board, depth - 2, -beta, -alpha, not maximizing_player, start_time, time_limit, current_depth + 1)
                if score > alpha:
                    score = -alphabeta(board, depth - 1, -beta, -alpha, not maximizing_player, start_time, time_limit, current_depth + 1)
            else:
                score = -alphabeta(board, depth - 1, -beta, -alpha, not maximizing_player, start_time, time_limit, current_depth + 1)
        except TimeoutError:
            board.pop()
            raise TimeoutError
        board.pop()
        if score > best_val:
            best_val = score
            best_move = move
        alpha = max(alpha, score)
        if alpha >= beta:
            if not board.is_capture(move):
                if move != killer_moves[current_depth][0]:
                    killer_moves[current_depth][1] = killer_moves[current_depth][0]
                    killer_moves[current_depth][0] = move
                history_key = (board.turn, move.from_square, move.to_square)
                history_table[history_key] = history_table.get(history_key, 0) + depth * depth
            break
    tt_type = 'exact'
    if best_val <= original_alpha: tt_type = 'upper'
    elif best_val >= beta: tt_type = 'lower'
    transposition_table[board_hash] = {'score': best_val, 'depth': depth, 'type': tt_type, 'move': best_move}
    return best_val

def next_move(fen):
    board = chess.Board(fen)
    start_time = time.time()
    time_limit = 3.6
    best_move = None
    moves = list(board.legal_moves)
    if not moves: return None
    max_depth = 40
    global killer_moves
    if len(killer_moves) < max_depth:
        killer_moves = [[None, None] for _ in range(max_depth)]
    else:
        for i in range(len(killer_moves)): killer_moves[i] = [None, None]
    try:
        for depth in range(1, max_depth):
            alpha, beta = -float('inf'), float('inf')
            moves.sort(key=lambda m: move_priority(board, m, 0), reverse=True)
            best_val = -float('inf')
            current_best_move = None
            for move in moves:
                board.push(move)
                val = -alphabeta(board, depth - 1, -beta, -alpha, board.turn == chess.BLACK, start_time, time_limit, 1)
                board.pop()
                if val > best_val:
                    best_val = val
                    current_best_move = move
                alpha = max(alpha, val)
            if current_best_move: best_move = current_best_move
    except TimeoutError: pass
    if best_move is None: best_move = moves[0]
    return str(best_move)
