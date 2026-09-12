import chess
import random
import time

# ─── Constants ────────────────────────────────────────────────────────────────
TIME_LIMIT = 3.4   
MAX_DEPTH  = 8
INF        = 10_000_000

# ─── Piece values ─────────────────────────────────────────────────────────────
PIECE_VALUE = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   0,
}

# ─── Piece-square tables (white's perspective, a1=index 0) ───────────────────
# Tables are indexed [square] where square follows python-chess convention:
# a1=0, b1=1, …, h8=63  (rank-major, so rank 1 is indices 0-7)
# We store them rank 8→1 top-to-bottom for readability, then reverse.

def _mk(rows):
    """rows given rank8…rank1 (top→bottom), return list indexed a1=0…h8=63"""
    flat = []
    for row in reversed(rows):   # reverse so rank1 becomes indices 0-7
        flat.extend(row)
    return flat

PAWN_TABLE = _mk([
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [ 5,  5, 10, 25, 25, 10,  5,  5],
    [ 0,  0,  0, 20, 20,  0,  0,  0],
    [ 5, -5,-10,  0,  0,-10, -5,  5],
    [ 5, 10, 10,-20,-20, 10, 10,  5],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
])

KNIGHT_TABLE = _mk([
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50],
])

BISHOP_TABLE = _mk([
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20],
])

ROOK_TABLE = _mk([
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [ 0,  0,  0,  5,  5,  0,  0,  0],
])

QUEEN_TABLE = _mk([
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20],
])

KING_MID_TABLE = _mk([
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20],
])

PIECE_TABLE = {
    chess.PAWN:   PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK:   ROOK_TABLE,
    chess.QUEEN:  QUEEN_TABLE,
    chess.KING:   KING_MID_TABLE,
}

# ─── Evaluation ───────────────────────────────────────────────────────────────

def piece_square(piece_type, square, color):
    table = PIECE_TABLE[piece_type]
    if color == chess.WHITE:
        return table[square]
    else:
        # mirror vertically for black
        rank = square >> 3
        file = square & 7
        mirrored = (7 - rank) * 8 + file
        return table[mirrored]

def evaluate(board):
    """Return score from the perspective of the side to move."""
    if board.is_checkmate():
        return -INF + board.fullmove_number   # sooner mate is worse for loser
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for sq, piece in board.piece_map().items():
        val = PIECE_VALUE[piece.piece_type] + piece_square(piece.piece_type, sq, piece.color)
        if piece.color == chess.WHITE:
            score += val
        else:
            score -= val

    # Return from perspective of side to move
    return score if board.turn == chess.WHITE else -score

# ─── Move ordering ────────────────────────────────────────────────────────────

def move_score(board, move):
    score = 0
    # Captures: MVV-LVA 
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        v_val = PIECE_VALUE.get(victim.piece_type, 0) if victim else 0
        a_val = PIECE_VALUE.get(attacker.piece_type, 100) if attacker else 100
        score += 10 * v_val - a_val + 20_000   # captures always first
    # Promotions
    if move.promotion:
        score += PIECE_VALUE.get(move.promotion, 0) + 15_000
    # Checks (cheap approximation — actual legality already guaranteed)
    board.push(move)
    if board.is_check():
        score += 5_000
    board.pop()
    return score

def ordered_moves(board):
    moves = list(board.legal_moves)
    try:
        moves.sort(key=lambda m: move_score(board, m), reverse=True)
    except Exception:
        pass
    return moves

# ─── Quiescence search ────────────────────────────────────────────────────────

def quiescence(board, alpha, beta, start_time):
    if time.time() - start_time > TIME_LIMIT:
        return evaluate(board)

    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    for move in board.legal_moves:
        if not board.is_capture(move) and not move.promotion:
            continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha, start_time)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

# ─── Negamax with alpha-beta ──────────────────────────────────────────────────

def negamax(board, depth, alpha, beta, start_time):
    if time.time() - start_time > TIME_LIMIT:
        raise TimeoutError

    if board.is_game_over():
        if board.is_checkmate():
            return -INF + board.fullmove_number
        return 0

    if depth == 0:
        return quiescence(board, alpha, beta, start_time)

    for move in ordered_moves(board):
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha, start_time)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

# ─── Iterative deepening ──────────────────────────────────────────────────────

def next_move(fen: str) -> str:
    start_time = time.time()
    try:
        board = chess.Board(fen)
        legal = list(board.legal_moves)
        if not legal:
            return None  
            
        # Fallback: first legal move (updated as search completes each depth)
        best_move = legal[0]

        for depth in range(1, MAX_DEPTH + 1):
            if time.time() - start_time > TIME_LIMIT:
                break

            current_best = None
            current_best_score = -INF
            alpha = -INF
            beta  =  INF
            timed_out = False

            for move in ordered_moves(board):
                if time.time() - start_time > TIME_LIMIT:
                    timed_out = True
                    break
                board.push(move)
                try:
                    score = -negamax(board, depth - 1, -beta, -alpha, start_time)
                except TimeoutError:
                    board.pop()
                    timed_out = True
                    break
                board.pop()
                if score > current_best_score:
                    current_best_score = score
                    current_best = move
                if score > alpha:
                    alpha = score

            # Only update best_move if we completed this depth fully
            if not timed_out and current_best is not None:
                best_move = current_best

            if timed_out:
                break

        return best_move.uci()

    except Exception:
        # Ultimate fallback: random legal move
        try:
            board = chess.Board(fen)
            moves = list(board.legal_moves)
            if moves:
                return random.choice(moves).uci()
        except Exception:
            pass
        return None
