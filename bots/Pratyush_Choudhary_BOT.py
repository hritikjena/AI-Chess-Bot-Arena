"""
╔══════════════════════════════════════════════════════════════╗
║              CHESS BOT — COMPETITION EDITION                ║
║         Negamax + Alpha-Beta + Iterative Deepening          ║
║     Transposition Table | Move Ordering | Quiescence        ║
║         Null-Move Pruning | LMR | PST Evaluation           ║
╚══════════════════════════════════════════════════════════════╝
"""

import chess
import time
import random

# ═══════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════

TIME_LIMIT = 3.4          # seconds (safe margin below 4 s)
MAX_DEPTH   = 30          # iterative deepening ceiling
TT_MAX_SIZE = 1 << 21    # ~2 M transposition table entries

# ═══════════════════════════════════════════════════════════════
#  PIECE VALUES  (centipawns)
# ═══════════════════════════════════════════════════════════════

PIECE_VALUE = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:  20000,
}

# ═══════════════════════════════════════════════════════════════
#  PIECE-SQUARE TABLES
#  Layout: index 0 = a8, index 7 = h8, index 56 = a1, index 63 = h1
#  (Standard chess table orientation, rank-8 to rank-1, file-a to file-h)
#  For WHITE  → pst_index = (7 - rank) * 8 + file   (flip rank)
#  For BLACK  → pst_index = rank * 8 + file          (mirror naturally)
# ═══════════════════════════════════════════════════════════════

PST_PAWN = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 27, 27, 10,  5,  5,
     0,  0,  0, 25, 25,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-25,-25, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

PST_KNIGHT = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

PST_BISHOP = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

PST_ROOK = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

PST_QUEEN = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

PST_KING_MID = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

PST_KING_END = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

# Lookup dict for non-king pieces
PST = {
    chess.PAWN:   PST_PAWN,
    chess.KNIGHT: PST_KNIGHT,
    chess.BISHOP: PST_BISHOP,
    chess.ROOK:   PST_ROOK,
    chess.QUEEN:  PST_QUEEN,
}

# ═══════════════════════════════════════════════════════════════
#  OPENING BOOK  (common strong replies, chosen at random)
# ═══════════════════════════════════════════════════════════════

OPENING_BOOK = {
    # Starting position → e4 / d4 / Nf3 / c4
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
        "e2e4","d2d4","g1f3","c2c4"
    ],
    # After 1.e4 → e5 / c5 / e6 / c6
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": [
        "e7e5","c7c5","e7e6","c7c6"
    ],
    # After 1.d4 → d5 / Nf6 / e6 / c5
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1": [
        "d7d5","g8f6","e7e6","c7c5"
    ],
    # After 1.c4 → e5 / c5 / Nf6
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1": [
        "e7e5","c7c5","g8f6"
    ],
    # After 1.Nf3 → d5 / Nf6 / c5
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": [
        "d7d5","g8f6","c7c5"
    ],
}

# ═══════════════════════════════════════════════════════════════
#  GLOBAL SEARCH STATE
# ═══════════════════════════════════════════════════════════════

# Transposition table: zobrist_key → (depth, flag, score, best_move)
# flag: 0 = EXACT, 1 = LOWER_BOUND, 2 = UPPER_BOUND
TT: dict = {}

# Killer moves: [ply][slot 0|1]
KILLERS: list = [[None, None] for _ in range(128)]

# History heuristic: (from_sq, to_sq) → cumulative score
HISTORY: dict = {}

# Nodes searched (diagnostic)
NODES: int = 0

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _pst_idx(square: int, color: chess.Color) -> int:
    """PST index for a square, mirrored per side."""
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    if color == chess.WHITE:
        return (7 - rank) * 8 + file   # flip rank for white
    return rank * 8 + file             # keep rank for black

def _endgame_phase(board: chess.Board) -> float:
    """
    Returns a value in [0, 1].
    0 = full middlegame, 1 = full endgame.
    Based on total non-pawn material remaining.
    """
    npm = 0
    for pt in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
        npm += (len(board.pieces(pt, chess.WHITE)) +
                len(board.pieces(pt, chess.BLACK))) * PIECE_VALUE[pt]
    # ~7700 cp at game start → scale to 0..1
    return max(0.0, 1.0 - npm / 3900.0)

# ═══════════════════════════════════════════════════════════════
#  STATIC EVALUATION
#  Always returns score from WHITE's absolute perspective.
#  Positive  →  White is better.
#  Negative  →  Black is better.
# ═══════════════════════════════════════════════════════════════

def evaluate(board: chess.Board) -> int:
    # Terminal states
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if (board.is_stalemate() or board.is_insufficient_material() or
            board.is_fifty_moves() or board.is_fivefold_repetition()):
        return 0

    eg = _endgame_phase(board)
    score = 0

    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1

        # ── Material + PST ──────────────────────────────────────
        for pt, table in PST.items():
            for sq in board.pieces(pt, color):
                score += sign * (PIECE_VALUE[pt] + table[_pst_idx(sq, color)])

        # ── King (interpolated mid/end) ─────────────────────────
        for sq in board.pieces(chess.KING, color):
            idx = _pst_idx(sq, color)
            k = PST_KING_MID[idx] * (1 - eg) + PST_KING_END[idx] * eg
            score += sign * int(k)

        # ── Bishop pair bonus ───────────────────────────────────
        if len(board.pieces(chess.BISHOP, color)) >= 2:
            score += sign * 35

        # ── Rooks on open / semi-open files ────────────────────
        for sq in board.pieces(chess.ROOK, color):
            f = chess.square_file(sq)
            own = sum(1 for s in board.pieces(chess.PAWN, color)
                      if chess.square_file(s) == f)
            opp = sum(1 for s in board.pieces(chess.PAWN, not color)
                      if chess.square_file(s) == f)
            if own == 0:
                score += sign * (25 if opp == 0 else 12)

        # ── Pawn structure ──────────────────────────────────────
        pawn_files = [chess.square_file(s) for s in board.pieces(chess.PAWN, color)]
        for f in range(8):
            cnt = pawn_files.count(f)
            if cnt > 1:
                score -= sign * 20 * (cnt - 1)         # doubled
            if cnt > 0:
                has_left  = (f > 0 and (f - 1) in pawn_files)
                has_right = (f < 7 and (f + 1) in pawn_files)
                if not has_left and not has_right:
                    score -= sign * 15                  # isolated

        # ── Passed pawns ────────────────────────────────────────
        for sq in board.pieces(chess.PAWN, color):
            if _is_passed(board, sq, color):
                rank = chess.square_rank(sq)
                advancement = rank if color == chess.WHITE else 7 - rank
                score += sign * (10 + advancement * 18)

        # ── King safety (middlegame only) ───────────────────────
        if eg < 0.6:
            king_sq = board.king(color)
            if king_sq is not None:
                # Pawn shield in front of king
                shield = _pawn_shield(board, king_sq, color)
                score += sign * int(shield * (1 - eg))

    # ── Tempo / mobility ────────────────────────────────────────
    mob = board.legal_moves.count()
    score += (1 if board.turn == chess.WHITE else -1) * mob * 5

    return score


def _is_passed(board: chess.Board, sq: int, color: chess.Color) -> bool:
    """True if pawn on sq has no opposing pawns blocking or attacking on its path."""
    file = chess.square_file(sq)
    rank = chess.square_rank(sq)
    enemy = not color
    r_range = range(rank + 1, 8) if color == chess.WHITE else range(0, rank)
    for r in r_range:
        for f in range(max(0, file - 1), min(8, file + 2)):
            s = chess.square(f, r)
            p = board.piece_at(s)
            if p and p.piece_type == chess.PAWN and p.color == enemy:
                return False
    return True


def _pawn_shield(board: chess.Board, king_sq: int, color: chess.Color) -> int:
    """Simple pawn shield: count pawns in the 3 squares directly in front of king."""
    bonus = 0
    kfile = chess.square_file(king_sq)
    krank = chess.square_rank(king_sq)
    direction = 1 if color == chess.WHITE else -1
    for df in (-1, 0, 1):
        f = kfile + df
        r = krank + direction
        if 0 <= f <= 7 and 0 <= r <= 7:
            s = chess.square(f, r)
            p = board.piece_at(s)
            if p and p.piece_type == chess.PAWN and p.color == color:
                bonus += 10
    return bonus

# ═══════════════════════════════════════════════════════════════
#  MOVE ORDERING
# ═══════════════════════════════════════════════════════════════

def _mvv_lva(board: chess.Board, move: chess.Move) -> int:
    """Most-Valuable-Victim / Least-Valuable-Attacker score for captures."""
    victim   = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)
    vv = PIECE_VALUE[victim.piece_type]   if victim   else PIECE_VALUE[chess.PAWN]
    av = PIECE_VALUE[attacker.piece_type] if attacker else 0
    return vv * 10 - av


def _score_move(board: chess.Board, move: chess.Move,
                ply: int, tt_move) -> int:
    """Assign a priority score to a move for ordering."""
    if move == tt_move:
        return 10_000_000
    if board.is_capture(move):
        return 1_000_000 + _mvv_lva(board, move)
    if move.promotion:
        return 900_000 + PIECE_VALUE.get(move.promotion, 0)
    if ply < 128:
        if move == KILLERS[ply][0]:
            return 800_000
        if move == KILLERS[ply][1]:
            return 700_000
    return HISTORY.get((move.from_square, move.to_square), 0)


def _order(board: chess.Board, moves, ply: int, tt_move=None):
    return sorted(moves,
                  key=lambda m: _score_move(board, m, ply, tt_move),
                  reverse=True)

# ═══════════════════════════════════════════════════════════════
#  QUIESCENCE SEARCH
#  Extends the search on captures to avoid the horizon effect.
# ═══════════════════════════════════════════════════════════════

def quiesce(board: chess.Board, alpha: int, beta: int, start: float) -> int:
    global NODES
    NODES += 1

    if time.time() - start > TIME_LIMIT:
        raise TimeoutError()

    # Stand-pat score (from current player's perspective)
    raw = evaluate(board)
    stand_pat = raw if board.turn == chess.WHITE else -raw

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    # Delta pruning: skip if even winning the queen won't help
    DELTA = 900 + 200  # queen + safety margin
    if stand_pat + DELTA < alpha:
        return alpha

    captures = [m for m in board.legal_moves if board.is_capture(m)]
    captures = _order(board, captures, 0)

    for move in captures:
        board.push(move)
        score = -quiesce(board, -beta, -alpha, start)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

# ═══════════════════════════════════════════════════════════════
#  NEGAMAX WITH ALPHA-BETA PRUNING
#  Returns score from the current player's perspective.
# ═══════════════════════════════════════════════════════════════

def negamax(board: chess.Board, depth: int, alpha: int, beta: int,
            start: float, ply: int = 0, allow_null: bool = True) -> int:
    global NODES, TT
    NODES += 1

    # ── Time guard ──────────────────────────────────────────────
    if time.time() - start > TIME_LIMIT:
        raise TimeoutError()

    # ── Terminal checks ─────────────────────────────────────────
    if board.is_checkmate():
        return -(99999 - ply)      # prefer closer mates
    if (board.is_stalemate() or board.is_insufficient_material() or
            board.is_fifty_moves() or board.is_fivefold_repetition()):
        return 0

    # ── Transposition table lookup ───────────────────────────────
    key = board._transposition_key()
    tt_entry = TT.get(key)
    tt_move  = None
    if tt_entry is not None:
        tt_depth, tt_flag, tt_score, tt_move = tt_entry
        if tt_depth >= depth:
            if tt_flag == 0:                  # EXACT
                return tt_score
            elif tt_flag == 1:                # LOWER_BOUND
                alpha = max(alpha, tt_score)
            else:                             # UPPER_BOUND
                beta  = min(beta,  tt_score)
            if alpha >= beta:
                return tt_score

    # ── Quiescence at horizon ────────────────────────────────────
    if depth <= 0:
        return quiesce(board, alpha, beta, start)

    in_check = board.is_check()

    # ── Check extension ──────────────────────────────────────────
    if in_check:
        depth += 1

    # ── Null-move pruning ────────────────────────────────────────
    if (allow_null and depth >= 3 and not in_check and
            _has_non_pawn_material(board, board.turn)):
        R = 3 if depth >= 6 else 2
        board.push(chess.Move.null())
        null_score = -negamax(board, depth - R - 1, -beta, -beta + 1,
                              start, ply + 1, False)
        board.pop()
        if null_score >= beta:
            return beta

    # ── Futility pruning ─────────────────────────────────────────
    raw = evaluate(board)
    static = raw if board.turn == chess.WHITE else -raw
    FUTILITY_MARGIN = [0, 150, 300, 500]
    if (depth <= 3 and not in_check and
            static + FUTILITY_MARGIN[depth] <= alpha):
        return quiesce(board, alpha, beta, start)

    # ── Main move loop ───────────────────────────────────────────
    moves = list(board.legal_moves)
    if not moves:
        return 0   # should be handled above, safety net

    moves = _order(board, moves, ply, tt_move)

    orig_alpha = alpha
    best_score = -100_000
    best_move  = moves[0]

    for i, move in enumerate(moves):
        board.push(move)

        # Late Move Reductions (LMR)
        if (i >= 3 and depth >= 3 and not in_check and
                not board.is_check() and
                not board.is_capture(move) and
                not move.promotion):
            r = max(1, int(depth ** 0.5 + i ** 0.5) - 1)
            score = -negamax(board, depth - 1 - r, -alpha - 1, -alpha,
                             start, ply + 1)
            if alpha < score < beta:
                score = -negamax(board, depth - 1, -beta, -alpha,
                                 start, ply + 1)
        elif i > 0:
            # Principal Variation Search: narrow window for non-PV nodes
            score = -negamax(board, depth - 1, -alpha - 1, -alpha,
                             start, ply + 1)
            if alpha < score < beta:
                score = -negamax(board, depth - 1, -beta, -alpha,
                                 start, ply + 1)
        else:
            score = -negamax(board, depth - 1, -beta, -alpha,
                             start, ply + 1)

        board.pop()

        if score > best_score:
            best_score = score
            best_move  = move

        if score > alpha:
            alpha = score

        if alpha >= beta:
            # Update killer and history tables
            if not board.is_capture(move) and ply < 128:
                KILLERS[ply][1] = KILLERS[ply][0]
                KILLERS[ply][0] = move
                HISTORY[(move.from_square, move.to_square)] = (
                    HISTORY.get((move.from_square, move.to_square), 0) +
                    depth * depth
                )
            break

    # ── Store in transposition table ─────────────────────────────
    if best_score <= orig_alpha:
        flag = 2   # UPPER_BOUND
    elif best_score >= beta:
        flag = 1   # LOWER_BOUND
    else:
        flag = 0   # EXACT

    # Limit TT size
    if len(TT) >= TT_MAX_SIZE:
        TT.clear()
    TT[key] = (depth, flag, best_score, best_move)

    return best_score


def _has_non_pawn_material(board: chess.Board, color: chess.Color) -> bool:
    """True if the side has at least one piece other than king and pawns."""
    for pt in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
        if board.pieces(pt, color):
            return True
    return False

# ═══════════════════════════════════════════════════════════════
#  ITERATIVE DEEPENING ROOT SEARCH
# ═══════════════════════════════════════════════════════════════

def _search(board: chess.Board, start: float) -> chess.Move:
    global NODES, KILLERS, HISTORY

    NODES   = 0
    KILLERS = [[None, None] for _ in range(128)]
    HISTORY = {}

    legal = list(board.legal_moves)
    if not legal:
        return None
    if len(legal) == 1:
        return legal[0]

    best_move  = legal[0]
    best_score = -100_000

    for depth in range(1, MAX_DEPTH + 1):
        if time.time() - start > TIME_LIMIT * 0.6:
            break

        try:
            # Aspiration windows (widen on failure)
            window = 50
            a = best_score - window
            b = best_score + window

            while True:
                try:
                    depth_best  = None
                    depth_score = -100_000
                    moves = _order(board, legal, 0, None)

                    for move in moves:
                        if time.time() - start > TIME_LIMIT * 0.9:
                            raise TimeoutError()

                        board.push(move)
                        score = -negamax(board, depth - 1, -b, -a, start, 1)
                        board.pop()

                        if score > depth_score:
                            depth_score = score
                            depth_best  = move

                        if score > a:
                            a = score

                        if a >= b:
                            break

                    # Aspiration result
                    if depth_score <= a - window:
                        b = a + window
                        a = depth_score - window
                    elif depth_score >= b - window:
                        a = b - window
                        b = depth_score + window
                    else:
                        break   # within window → accept

                except TimeoutError:
                    raise

            if depth_best is not None:
                best_move  = depth_best
                best_score = depth_score

        except TimeoutError:
            break

    return best_move

# ═══════════════════════════════════════════════════════════════
#  PUBLIC API  — called by the competition server
# ═══════════════════════════════════════════════════════════════

def next_move(fen: str) -> str:
    """
    Receive the board as FEN, return the best move in UCI notation.
    This is the only function the server calls.
    """
    start = time.time()
    board = chess.Board(fen)

    # ── Opening book ─────────────────────────────────────────────
    book = OPENING_BOOK.get(fen)
    if book:
        return random.choice(book)

    # ── Search ───────────────────────────────────────────────────
    best = _search(board, start)
    elapsed = time.time() - start

    if best is None:
        legal = list(board.legal_moves)
        if not legal:
            return ""
        best = legal[0]

    return str(best)


# ═══════════════════════════════════════════════════════════════
#  SELF-TEST  (run directly to verify bot works)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  CHESS BOT — SELF TEST")
    print("=" * 60)

    test_positions = [
        ("Starting position",
         "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),

        ("Mid-game (Ruy Lopez)",
         "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"),

        ("Tactical puzzle (white to play, mate in 1)",
         "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4"),

        ("Endgame — king and pawn",
         "8/8/8/3k4/8/8/3PK3/8 w - - 0 1"),

        ("Complex tactical",
         "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"),
    ]

    board_tmp = chess.Board()
    for name, fen in test_positions:
        board_tmp.set_fen(fen)
        t0 = time.time()
        move = next_move(fen)
        elapsed = time.time() - t0
        print(f"\n[{name}]")
        print(f"  FEN   : {fen}")
        print(f"  Move  : {move}")
        print(f"  Time  : {elapsed:.3f}s")
        # Validate
        board_tmp.set_fen(fen)
        try:
            m = chess.Move.from_uci(move)
            valid = m in board_tmp.legal_moves
        except Exception:
            valid = False
        print(f"  Valid : {'✓ YES' if valid else '✗ ILLEGAL — BUG!'}")

    print("\n" + "=" * 60)
    print("  All tests complete.")
    print("=" * 60)
