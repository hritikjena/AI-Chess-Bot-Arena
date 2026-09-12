import chess
import time

# ──────────────────────────────────────────────
# Piece values (centipawns)
# ──────────────────────────────────────────────
PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   20000,
}

# ──────────────────────────────────────────────
# Piece-Square Tables (from White's perspective)
# Encourages good piece placement
# ──────────────────────────────────────────────
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_MIDGAME_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

KING_ENDGAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

PST = {
    chess.PAWN:   PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK:   ROOK_TABLE,
    chess.QUEEN:  QUEEN_TABLE,
    chess.KING:   KING_MIDGAME_TABLE,   # switched in endgame
}

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def is_endgame(board: chess.Board) -> bool:
    """Simple endgame detection: queens gone or very little material."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + \
             len(board.pieces(chess.QUEEN, chess.BLACK))
    minor = sum(
        len(board.pieces(pt, c))
        for pt in (chess.ROOK, chess.BISHOP, chess.KNIGHT)
        for c in (chess.WHITE, chess.BLACK)
    )
    return queens == 0 or (queens == 2 and minor <= 2)


def pst_score(piece_type, square, color, endgame):
    """Return piece-square table bonus for a piece."""
    table = KING_ENDGAME_TABLE if (piece_type == chess.KING and endgame) else PST[piece_type]
    # Table is stored from White's visual perspective (rank 8 first)
    idx = square if color == chess.WHITE else chess.square_mirror(square)
    # Table index: rank 7 → row 0, rank 0 → row 7 visually
    rank = 7 - chess.square_rank(idx)
    file = chess.square_file(idx)
    return table[rank * 8 + file]


def evaluate(board: chess.Board) -> int:
    """
    Static evaluation from the perspective of the side to move.
    Positive = better for the side to move.
    """
    if board.is_checkmate():
        return -100000  # side to move is mated
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    endgame = is_endgame(board)
    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        value = PIECE_VALUES[piece.piece_type]
        positional = pst_score(piece.piece_type, square, piece.color, endgame)
        total = value + positional
        if piece.color == chess.WHITE:
            score += total
        else:
            score -= total

    # Mobility bonus (small)
    score += len(list(board.legal_moves)) * 5
    board.push(chess.Move.null())          # switch side
    score -= len(list(board.legal_moves)) * 5
    board.pop()

    # Return from side-to-move perspective
    return score if board.turn == chess.WHITE else -score


# ──────────────────────────────────────────────
# Move ordering — improves alpha-beta efficiency
# ──────────────────────────────────────────────

def move_score(board: chess.Board, move: chess.Move) -> int:
    """Heuristic score for move ordering (higher = search first)."""
    s = 0
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            # MVV-LVA: Most Valuable Victim – Least Valuable Attacker
            s += 10 * PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
    if move.promotion:
        s += PIECE_VALUES[move.promotion]
    if board.gives_check(move):
        s += 50
    return s


def ordered_moves(board: chess.Board):
    return sorted(board.legal_moves, key=lambda m: move_score(board, m), reverse=True)


# ──────────────────────────────────────────────
# Alpha-Beta Minimax
# ──────────────────────────────────────────────

def alphabeta(board: chess.Board, depth: int, alpha: int, beta: int,
              deadline: float) -> int:
    """Negamax with alpha-beta pruning and time cutoff."""
    if time.time() > deadline:
        raise TimeoutError

    if depth == 0 or board.is_game_over():
        return quiesce(board, alpha, beta, deadline)

    for move in ordered_moves(board):
        board.push(move)
        score = -alphabeta(board, depth - 1, -beta, -alpha, deadline)
        board.pop()
        if score >= beta:
            return beta          # beta cut-off
        if score > alpha:
            alpha = score

    return alpha


def quiesce(board: chess.Board, alpha: int, beta: int, deadline: float) -> int:
    """Quiescence search: only look at captures to avoid horizon effect."""
    if time.time() > deadline:
        raise TimeoutError

    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    for move in ordered_moves(board):
        if not board.is_capture(move):
            continue
        board.push(move)
        score = -quiesce(board, -beta, -alpha, deadline)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# ──────────────────────────────────────────────
# Iterative Deepening — maximises depth in time
# ──────────────────────────────────────────────

def best_move(board: chess.Board, time_limit: float = 3.0) -> chess.Move:
    """
    Iterative deepening alpha-beta.
    Searches deeper and deeper until time runs out,
    always keeping the best move found so far.
    """
    deadline = time.time() + time_limit
    moves = list(board.legal_moves)

    if not moves:
        return None

    best = moves[0]          # fallback: any legal move

    for depth in range(1, 20):
        if time.time() >= deadline:
            break
        try:
            current_best = None
            current_best_score = -10**9
            alpha = -10**9
            beta = 10**9

            for move in ordered_moves(board):
                board.push(move)
                score = -alphabeta(board, depth - 1, -beta, -alpha, deadline)
                board.pop()
                if score > current_best_score:
                    current_best_score = score
                    current_best = move
                alpha = max(alpha, score)

            if current_best:
                best = current_best   # only update if full depth completed

        except TimeoutError:
            break   # time's up — use last fully-completed depth result

    return best


# ──────────────────────────────────────────────
# Entry point required by the arena
# ──────────────────────────────────────────────

def next_move(fen: str) -> str:
    board = chess.Board(fen)
    move = best_move(board, time_limit=3.0)   # 3 s budget, 1 s safety margin
    return str(move)


# ──────────────────────────────────────────────
# Quick local test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    test_fen = chess.STARTING_FEN
    print("Board:")
    print(chess.Board(test_fen))
    print("\nBot move:", next_move(test_fen))