import chess
import chess.polyglot
import time
import random

PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   20000,
}

# SEE uses a flat array indexed by piece type (0-6)
SEE_VALUES = [0, 100, 320, 330, 500, 900, 20000]  # index = piece_type

# ───────────────────────────────────────────────────────────────────
#  PIECE-SQUARE TABLES
# ───────────────────────────────────────────────────────────────────
# fmt: off
_PST_PAWN_MG = [
     0,  0,  0,  0,  0,  0,  0,  0,
    98,134, 61, 95, 68,126, 34,-11,
    -6,  7, 26, 31, 65, 56, 25,-20,
   -14, 13,  6, 21, 23, 12, 17,-23,
   -27, -2, -5, 12, 17,  6, 10,-25,
   -26, -4, -4,-10,  3,  3, 33,-12,
   -35, -1,-20,-23,-15, 24, 38,-22,
     0,  0,  0,  0,  0,  0,  0,  0,
]
_PST_PAWN_EG = [
     0,  0,  0,  0,  0,  0,  0,  0,
   178,173,158,134,147,132,165,187,
    94,100, 85, 67, 56, 53, 82, 84,
    32, 24, 13,  5, -2,  4, 17, 17,
    13,  9, -3, -7, -7, -8,  3, -1,
     4,  7, -6,  1,  0, -5, -1, -8,
    13,  8,  8, 10, 13,  0,  2, -7,
     0,  0,  0,  0,  0,  0,  0,  0,
]
_PST_KNIGHT = [
  -167,-89,-34,-49, 61,-97,-15,-107,
   -73,-41, 72, 36, 23, 62,  7, -17,
   -47, 60, 37, 65, 84,129, 73,  44,
    -9, 17, 19, 53, 37, 69, 18,  22,
   -13,  4, 16, 13, 28, 19, 21,  -8,
   -23, -9, 12, 10, 19, 17, 25, -16,
   -29,-53,-12, -3, -1, 18,-14, -19,
  -105,-21,-58,-33,-17,-28,-19, -23,
]
_PST_BISHOP_MG = [
   -29,  4,-82,-37,-25,-42,  7, -8,
   -26, 16,-18,-13, 30, 59, 18,-47,
   -16, 37, 43, 40, 35, 50, 37, -2,
    -4,  5, 19, 50, 37, 37,  7, -2,
    -6, 13, 13, 26, 34, 12, 10,  4,
     0, 15, 15, 15, 14, 27, 18, 10,
     4, 15, 16,  0,  7, 21, 33,  1,
   -33, -3,-14,-21,-13,-12,-39,-21,
]
_PST_ROOK_MG = [
    32, 42, 32, 51, 63,  9, 31, 43,
    27, 32, 58, 62, 80, 67, 26, 44,
    -5, 19, 26, 36, 17, 45, 61, 16,
   -24,-11,  7, 26, 24, 35, -8,-20,
   -36,-26,-12, -1,  9, -7,  6,-23,
   -45,-25,-16,-17,  3,  0, -5,-33,
   -44,-16,-20, -9, -1, 11, -6,-71,
   -19,-13,  1, 17, 16,  7,-37,-26,
]
_PST_QUEEN_MG = [
   -28,  0, 29, 12, 59, 44, 43, 45,
   -24,-39, -5,  1,-16, 57, 28, 54,
   -13,-17,  7,  8, 29, 56, 47, 57,
   -27,-27,-16,-16, -1, 17, -2,  1,
    -9,-26, -9,-10, -2, -4,  3, -3,
   -14,  2,-11, -2, -5,  2, 14,  5,
   -35, -8, 11,  2,  8, 15, -3,  1,
    -1,-18, -9, 10,-15,-25,-31,-50,
]
_PST_KING_MG = [
   -65, 23, 16,-15,-56,-34,  2, 13,
    29, -1,-20, -7, -8, -4,-38,-29,
    -9, 24,  2,-16,-20,  6, 22,-22,
   -17,-20,-12,-27,-30,-25,-14,-36,
   -49, -1,-27,-39,-46,-44,-33,-51,
   -14,-14,-22,-46,-44,-30,-15,-27,
     1,  7, -8,-64,-43,-16,  9,  8,
   -15, 36, 12,-54,  8,-28, 24, 14,
]
_PST_KING_EG = [
   -74,-35,-18,-18,-11, 15,  4,-17,
   -12, 17, 14, 17, 17, 38, 23, 11,
    10, 17, 23, 15, 20, 45, 44, 13,
    -8, 22, 24, 27, 26, 33, 26,  3,
   -18, -4, 21, 24, 27, 23,  9,-11,
   -19, -3, 11, 21, 23, 16,  7, -9,
   -27,-11,  4, 13, 14,  4, -5,-17,
   -53,-34,-21,-11,-28,-14,-24,-43,
]
# fmt: on

def _mirror(t):
    m = []
    for r in range(7, -1, -1):
        m.extend(t[r*8: r*8+8])
    return m

W, B = chess.WHITE, chess.BLACK

PST_MG = {
    W: {chess.PAWN:_PST_PAWN_MG, chess.KNIGHT:_PST_KNIGHT, chess.BISHOP:_PST_BISHOP_MG,
        chess.ROOK:_PST_ROOK_MG, chess.QUEEN:_PST_QUEEN_MG, chess.KING:_PST_KING_MG},
    B: {chess.PAWN:_mirror(_PST_PAWN_MG), chess.KNIGHT:_mirror(_PST_KNIGHT),
        chess.BISHOP:_mirror(_PST_BISHOP_MG), chess.ROOK:_mirror(_PST_ROOK_MG),
        chess.QUEEN:_mirror(_PST_QUEEN_MG), chess.KING:_mirror(_PST_KING_MG)},
}
PST_EG = {
    W: {chess.PAWN:_PST_PAWN_EG, chess.KNIGHT:_PST_KNIGHT, chess.BISHOP:_PST_BISHOP_MG,
        chess.ROOK:_PST_ROOK_MG, chess.QUEEN:_PST_QUEEN_MG, chess.KING:_PST_KING_EG},
    B: {chess.PAWN:_mirror(_PST_PAWN_EG), chess.KNIGHT:_mirror(_PST_KNIGHT),
        chess.BISHOP:_mirror(_PST_BISHOP_MG), chess.ROOK:_mirror(_PST_ROOK_MG),
        chess.QUEEN:_mirror(_PST_QUEEN_MG), chess.KING:_mirror(_PST_KING_EG)},
}

_PW = {chess.PAWN:0, chess.KNIGHT:1, chess.BISHOP:1,
       chess.ROOK:2, chess.QUEEN:4, chess.KING:0}
MAX_PHASE = 24


# ───────────────────────────────────────────────────────────────────
#  SEE  —  Static Exchange Evaluation
#
#  Returns the material gain/loss of making a capture on `to_sq`
#  with the piece on `from_sq`, accounting for all recaptures.
#  Positive = winning capture, Negative = losing capture.
# ───────────────────────────────────────────────────────────────────

def _lva(board, sq, side):
    """Return (least-valuable-attacker square, piece_type) for `side` on `sq`."""
    min_val = 99999
    min_sq  = None
    min_pt  = None
    for pt in (chess.PAWN, chess.KNIGHT, chess.BISHOP,
               chess.ROOK, chess.QUEEN, chess.KING):
        attackers = board.pieces(pt, side) & board.attackers(side, sq)
        if attackers:
            att_sq = next(iter(attackers))
            val    = SEE_VALUES[pt]
            if val < min_val:
                min_val = val
                min_sq  = att_sq
                min_pt  = pt
    return min_sq, min_pt


def see(board, move):
    """
    Static Exchange Evaluation for `move`.
    Returns centipawn gain (positive) or loss (negative).
    """
    to_sq   = move.to_square
    fr_sq   = move.from_square
    victim  = board.piece_at(to_sq)
    if victim is None:
        # En passant — victim is a pawn one rank away
        if board.is_en_passant(move):
            gain = SEE_VALUES[chess.PAWN]
        else:
            return 0
    else:
        gain = SEE_VALUES[victim.piece_type]

    attacker = board.piece_at(fr_sq)
    if attacker is None:
        return 0

    # Simulate the exchange on a copy
    b = board.copy(stack=False)
    b.push(move)

    # Recursively compute what the opponent gains by recapturing
    opp_gain = _see_rec(b, to_sq, attacker.piece_type, b.turn)
    return gain - opp_gain


def _see_rec(board, sq, last_pt, side):
    """Recursive SEE helper — return what `side` gains by capturing on `sq`."""
    att_sq, att_pt = _lva(board, sq, side)
    if att_sq is None:
        return 0   # no attacker left

    captured_val = SEE_VALUES[last_pt]

    # Make the capture on a copy
    b = board.copy(stack=False)
    capture = chess.Move(att_sq, sq)
    # Handle promotion (shouldn't happen often in SEE but be safe)
    if att_pt == chess.PAWN and chess.square_rank(sq) in (0, 7):
        capture = chess.Move(att_sq, sq, chess.QUEEN)
        att_pt = chess.QUEEN
    b.push(capture)

    # The opponent can recapture; we take the best outcome for ourselves
    opp = _see_rec(b, sq, att_pt, not side)
    return max(0, captured_val - opp)


def see_capture_ok(board, move, threshold=0):
    """True if the capture gains at least `threshold` centipawns."""
    return see(board, move) >= threshold



# ───────────────────────────────────────────────────────────────────
#  TRANSPOSITION TABLE
# ───────────────────────────────────────────────────────────────────
TT_SIZE = 1 << 21
TT_MASK = TT_SIZE - 1
_tt_key   = [0]    * TT_SIZE
_tt_depth = [-1]   * TT_SIZE
_tt_flag  = [0]    * TT_SIZE
_tt_score = [0]    * TT_SIZE
_tt_move  = [None] * TT_SIZE
TT_UPPER, TT_EXACT, TT_LOWER = 0, 1, 2

def tt_store(key, depth, flag, score, move):
    idx = key & TT_MASK
    if _tt_key[idx] != key or depth >= _tt_depth[idx]:
        _tt_key[idx]   = key
        _tt_depth[idx] = depth
        _tt_flag[idx]  = flag
        _tt_score[idx] = score
        _tt_move[idx]  = move

def tt_probe(key, depth, alpha, beta):
    idx = key & TT_MASK
    if _tt_key[idx] != key:
        return None, None
    move = _tt_move[idx]
    if _tt_depth[idx] < depth:
        return None, move
    score = _tt_score[idx]
    flag  = _tt_flag[idx]
    if flag == TT_EXACT:                    return score, move
    if flag == TT_LOWER and score >= beta:  return beta,  move
    if flag == TT_UPPER and score <= alpha: return alpha, move
    return None, move


# ───────────────────────────────────────────────────────────────────
#  PAWN HASH TABLE
# ───────────────────────────────────────────────────────────────────
PT_SIZE = 1 << 16
PT_MASK = PT_SIZE - 1
_pt_key   = [0] * PT_SIZE
_pt_score = [0] * PT_SIZE

def _pawn_hash(board):
    h = 0
    for sq in board.pieces(chess.PAWN, W): h ^= (1 << sq)
    for sq in board.pieces(chess.PAWN, B): h ^= (1 << (sq + 64))
    return h & 0xFFFFFFFFFFFFFFFF

def pt_probe(key):
    idx = key & PT_MASK
    return _pt_score[idx] if _pt_key[idx] == key else None

def pt_store(key, score):
    idx = key & PT_MASK
    _pt_key[idx]   = key
    _pt_score[idx] = score


# ───────────────────────────────────────────────────────────────────
#  KILLER MOVES + HISTORY
# ───────────────────────────────────────────────────────────────────
MAX_DEPTH = 14
killers  = [[None, None] for _ in range(MAX_DEPTH + 2)]
history  = [[0] * 64 for _ in range(64)]

def store_killer(move, ply):
    if ply <= MAX_DEPTH and move != killers[ply][0]:
        killers[ply][1] = killers[ply][0]
        killers[ply][0] = move

def is_killer(move, ply):
    return ply <= MAX_DEPTH and (move == killers[ply][0] or move == killers[ply][1])

def update_history(move, depth):
    history[move.from_square][move.to_square] += depth * depth


# ───────────────────────────────────────────────────────────────────
#  EVALUATION HELPERS
# ───────────────────────────────────────────────────────────────────

def game_phase(board):
    p = sum(_PW[pt] * (len(board.pieces(pt, W)) + len(board.pieces(pt, B))) for pt in _PW)
    return min(p, MAX_PHASE) / MAX_PHASE


def material_balance(board):
    """Quick White-relative material count (no PST)."""
    score = 0
    for color in (W, B):
        sign = 1 if color == W else -1
        for pt in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
            score += sign * PIECE_VALUES[pt] * len(board.pieces(pt, color))
    return score


def pawn_structure(board):
    """Cached pawn structure score (White-relative)."""
    ph = _pawn_hash(board)
    cached = pt_probe(ph)
    if cached is not None:
        return cached

    score = 0
    for color in (W, B):
        sign      = 1 if color == W else -1
        pawns     = board.pieces(chess.PAWN, color)
        opp_pawns = board.pieces(chess.PAWN, not color)
        own_files = set(chess.square_file(sq) for sq in pawns)
        opp_files = set(chess.square_file(sq) for sq in opp_pawns)

        for sq in pawns:
            f   = chess.square_file(sq)
            r   = chess.square_rank(sq)
            adj = {f-1, f+1} & set(range(8))

            # Doubled
            if sum(1 for s in pawns if chess.square_file(s) == f) > 1:
                score += sign * (-20)

            # Isolated
            if not (adj & own_files):
                score += sign * (-20)

            # Passed
            ahead = range(r+1, 8) if color == W else range(r-1, -1, -1)
            chk   = {f} | adj
            if not any(chess.square_file(s) in chk and chess.square_rank(s) in ahead
                       for s in opp_pawns):
                advance = r if color == W else (7 - r)
                score += sign * (20 + advance * 12)

    pt_store(ph, score)
    return score


# ───────────────────────────────────────────────────────────────────
#  ENDGAME K+P KNOWLEDGE
#
#  Covers three rules that classical search alone handles poorly:
#  1. Rule of the square — can enemy king catch a passed pawn?
#  2. Opposition — who controls the key squares?
#  3. Key squares — if your king reaches these, pawn promotes
# ───────────────────────────────────────────────────────────────────

def _chebyshev(sq1, sq2):
    """Max of file/rank distance — king moves needed."""
    return max(abs(chess.square_file(sq1) - chess.square_file(sq2)),
               abs(chess.square_rank(sq1) - chess.square_rank(sq2)))


def _key_squares(pawn_sq, color):
    """
    Key squares for a pawn: squares where if the own king stands,
    the pawn is guaranteed to promote regardless of enemy king.
    For a pawn on file f, rank r:
    - Ranks 2-5: two ranks ahead on same & adjacent files
    - Rank 6:    all three squares on the 7th rank ahead
    """
    f = chess.square_file(pawn_sq)
    r = chess.square_rank(pawn_sq)
    squares = []
    direction = 1 if color == W else -1
    target_ranks = [r + direction, r + 2 * direction]
    if color == W and r == 5:
        target_ranks = [6, 7]
    elif color == B and r == 2:
        target_ranks = [1, 0]
    for tr in target_ranks:
        for tf in range(max(0, f-1), min(8, f+2)):
            if 0 <= tr <= 7:
                squares.append(chess.square(tf, tr))
    return squares


def endgame_kp_bonus(board, color):
    """
    Extra score for K+P endgame patterns.
    Returns White-relative bonus.
    """
    sign     = 1 if color == W else -1
    pawns    = list(board.pieces(chess.PAWN, color))
    opp_pawns = board.pieces(chess.PAWN, not color)
    king_sq  = board.king(color)
    opp_king = board.king(not color)

    if king_sq is None or opp_king is None:
        return 0

    score = 0

    for pawn_sq in pawns:
        f = chess.square_file(pawn_sq)
        r = chess.square_rank(pawn_sq)

        # Only analyse passed pawns for these patterns
        ahead = range(r+1, 8) if color == W else range(r-1, -1, -1)
        adj   = {max(0, f-1), f, min(7, f+1)}
        is_passed = not any(
            chess.square_file(s) in adj and chess.square_rank(s) in ahead
            for s in opp_pawns
        )
        if not is_passed:
            continue

        # ── Rule of the square ──
        # If the opponent's king cannot enter the "square" of the pawn,
        # the pawn promotes no matter what (assuming the side to move pushes).
        promo_rank  = 7 if color == W else 0
        steps_to_promo = abs(promo_rank - r)
        opp_dist    = _chebyshev(opp_king, chess.square(f, promo_rank))
        # Adjust for whose turn it is
        bonus_to_move = 1 if board.turn == color else 0
        if opp_dist > steps_to_promo + (1 - bonus_to_move):
            # Opponent king can NEVER catch the pawn
            score += sign * (300 + steps_to_promo * 20)

        # ── Key squares ──
        for ks in _key_squares(pawn_sq, color):
            own_dist = _chebyshev(king_sq, ks)
            opp_dist_ks = _chebyshev(opp_king, ks)
            if own_dist < opp_dist_ks:
                score += sign * 40   # we control the key square

        # ── Opposition (direct) ──
        # When kings are on the same file/rank with one square between them
        kf, kr = chess.square_file(king_sq), chess.square_rank(king_sq)
        of, or_ = chess.square_file(opp_king), chess.square_rank(opp_king)
        if abs(kf - of) == 0 and abs(kr - or_) == 2:
            # Vertical opposition
            if board.turn == color:
                score += sign * 30   # we have opposition
            else:
                score -= sign * 30
        elif abs(kf - of) == 2 and abs(kr - or_) == 0:
            # Horizontal opposition
            if board.turn == color:
                score += sign * 20
            else:
                score -= sign * 20

    return score


def mobility_score(board, color):
    score = 0
    occ   = board.occupied
    for sq in board.pieces(chess.KNIGHT, color):
        score += bin(chess.BB_KNIGHT_ATTACKS[sq]).count('1') * 4
    for sq in board.pieces(chess.BISHOP, color):
        score += bin(chess.BB_DIAG_ATTACKS[sq][occ & chess.BB_DIAG_MASKS[sq]]).count('1') * 3
    for sq in board.pieces(chess.ROOK, color):
        score += bin(
            chess.BB_RANK_ATTACKS[sq][occ & chess.BB_RANK_MASKS[sq]] |
            chess.BB_FILE_ATTACKS[sq][occ & chess.BB_FILE_MASKS[sq]]
        ).count('1') * 2
    for sq in board.pieces(chess.QUEEN, color):
        score += bin(
            chess.BB_RANK_ATTACKS[sq][occ & chess.BB_RANK_MASKS[sq]] |
            chess.BB_FILE_ATTACKS[sq][occ & chess.BB_FILE_MASKS[sq]] |
            chess.BB_DIAG_ATTACKS[sq][occ & chess.BB_DIAG_MASKS[sq]]
        ).count('1')
    return score


def rook_bonus(board, color):
    score     = 0
    own_pawns = board.pieces(chess.PAWN, color)
    opp_pawns = board.pieces(chess.PAWN, not color)
    rooks     = list(board.pieces(chess.ROOK, color))
    seventh   = 6 if color == W else 1
    for sq in rooks:
        f = chess.square_file(sq)
        own_f = any(chess.square_file(p) == f for p in own_pawns)
        opp_f = any(chess.square_file(p) == f for p in opp_pawns)
        if not own_f and not opp_f: score += 20
        elif not own_f:             score += 10
        if chess.square_rank(sq) == seventh: score += 25
    if len(rooks) == 2:
        r0, r1 = rooks[0], rooks[1]
        between = chess.SquareSet(chess.between(r0, r1)) & board.occupied
        if (chess.square_rank(r0) == chess.square_rank(r1) or
                chess.square_file(r0) == chess.square_file(r1)) and not between:
            score += 15
    return score


def knight_outpost(board, color):
    score     = 0
    opp_pawns = board.pieces(chess.PAWN, not color)
    for sq in board.pieces(chess.KNIGHT, color):
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        if not (r >= 4 if color == W else r <= 3):
            continue
        adj = {f-1, f+1} & set(range(8))
        safe = not any(
            chess.square_file(s) in adj and
            (chess.square_rank(s) + 1 == r if color == B else chess.square_rank(s) - 1 == r)
            for s in opp_pawns
        )
        if safe:
            score += 15 + (r if color == W else 7-r) * 3
    return score


def king_safety(board, color, phase):
    if phase < 0.25:
        return 0
    king_sq = board.king(color)
    if king_sq is None:
        return 0
    score = 0
    kf    = chess.square_file(king_sq)
    kr    = chess.square_rank(king_sq)
    direction = 1 if color == W else -1

    # Pawn shield
    for df in (-1, 0, 1):
        nf, nr = kf+df, kr+direction
        if 0<=nf<=7 and 0<=nr<=7:
            s = chess.square(nf, nr)
            if board.piece_at(s) == chess.Piece(chess.PAWN, color):
                score += 10
        nf2, nr2 = kf+df, kr+2*direction
        if 0<=nf2<=7 and 0<=nr2<=7:
            s2 = chess.square(nf2, nr2)
            if board.piece_at(s2) == chess.Piece(chess.PAWN, color):
                score += 5

    # Open files near king
    own_pawns = board.pieces(chess.PAWN, color)
    opp_pawns = board.pieces(chess.PAWN, not color)
    for df in (-1, 0, 1):
        f = kf + df
        if not 0<=f<=7: continue
        own_f = any(chess.square_file(p)==f for p in own_pawns)
        opp_f = any(chess.square_file(p)==f for p in opp_pawns)
        if not own_f and not opp_f: score -= 25
        elif not own_f:             score -= 15

    # Attacker pressure
    for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq]):
        score -= len(board.attackers(not color, sq)) * 8

    # Castling rights penalty
    if phase > 0.5 and board.has_castling_rights(color):
        score -= 15

    return int(score * phase)


def bishop_pair(board, color):
    return 30 if len(board.pieces(chess.BISHOP, color)) >= 2 else 0


def evaluate(board):
    """
    Score from current side to move perspective (negamax).
    Positive = good for the side to move.
    """
    if board.is_checkmate():
        return -100000
    if board.is_stalemate():
        # Stalemate: WE gave the opponent a free draw — terrible!
        # Score it as a big penalty for the side that caused it
        # (the side that just moved, i.e., NOT board.turn)
        return -80000   # extremely bad — we stalemated them
    if board.is_insufficient_material() or board.can_claim_draw():
        return 0

    phase  = game_phase(board)
    mg, eg = 0, 0

    for color in (W, B):
        sign = 1 if color == W else -1
        for pt in PIECE_VALUES:
            for sq in board.pieces(pt, color):
                mg += sign * (PIECE_VALUES[pt] + PST_MG[color][pt][sq])
                eg += sign * (PIECE_VALUES[pt] + PST_EG[color][pt][sq])

    white_score = int(phase * mg + (1 - phase) * eg)
    white_score += pawn_structure(board)

    for color in (W, B):
        sign = 1 if color == W else -1
        white_score += sign * (
            mobility_score(board, color) +
            rook_bonus(board, color) +
            knight_outpost(board, color) +
            bishop_pair(board, color) +
            king_safety(board, color, phase)
        )

    # K+P endgame knowledge (only when few pieces remain)
    if phase < 0.4:
        for color in (W, B):
            white_score += endgame_kp_bonus(board, color)

    white_score += 10   # tempo

    # ── 50-move rule urgency ──
    # If halfmove clock is climbing, add penalty to force progress
    hmc = board.halfmove_clock
    if hmc > 30:
        # Urgency penalty: scale up as we approach 50
        urgency = (hmc - 30) * 15   # 0 at 30, 300 at 50
        white_score -= urgency if board.turn == W else -urgency

    # ── Move limit urgency (100 total moves = draw) ──
    # Encourage aggressive play when move count is rising
    total_moves = board.fullmove_number
    if total_moves > 35:
        # Push harder for checkmate — bonus for threatening king
        opp_king = board.king(not board.turn)
        if opp_king is not None:
            attackers = len(board.attackers(board.turn, opp_king))
            white_score += (1 if board.turn == W else -1) * attackers * 30

    return white_score if board.turn == W else -white_score


# ───────────────────────────────────────────────────────────────────
#  SMART REPETITION SCORING
#
#  Instead of always returning 0 for draws:
#  - If we're winning (score > threshold): repetition = bad (-contempt)
#  - If we're losing (score < -threshold): repetition = good (+contempt)
#  This stops the bot from "accidentally" agreeing to draws from won positions.
# ───────────────────────────────────────────────────────────────────
# ── ARENA DRAW AVOIDANCE ──────────────────────────────────────────
# Against weak bots (random/greedy/minimax-2), we are almost always
# winning. Any draw is a catastrophic result — avoid at all costs.
# Contempt = 500cp means we prefer losing 5 pawns over drawing.
CONTEMPT = 500

def draw_score(board):
    """
    Returns score for a drawn position from current side's perspective.
    We ALWAYS treat draws as very bad when we're ahead, because our
    opponents are weak and we should be winning every game.
    """
    mat = material_balance(board)
    our_mat = mat if board.turn == W else -mat
    # Even if slightly behind, we hate draws — we can outplay weak bots
    return -CONTEMPT if our_mat >= -200 else CONTEMPT // 2


# ───────────────────────────────────────────────────────────────────
#  MOVE ORDERING
# ───────────────────────────────────────────────────────────────────

def score_move(board, move, tt_move, ply):
    if move == tt_move:
        return 2_000_000

    if move.promotion == chess.QUEEN:
        return 1_900_000

    if board.is_capture(move):
        # Use SEE to distinguish winning from losing captures
        see_val = see(board, move)
        if see_val >= 0:
            # Winning/equal capture: order by SEE value
            return 1_500_000 + see_val
        else:
            # Losing capture: still try, but order last among captures
            return 800_000 + see_val

    if is_killer(move, ply):
        return 900_000 if move == killers[ply][0] else 899_000

    return history[move.from_square][move.to_square]


def ordered_moves(board, tt_move, ply):
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: score_move(board, m, tt_move, ply), reverse=True)
    return moves


# ───────────────────────────────────────────────────────────────────
#  QUIESCENCE SEARCH  (with SEE pruning)
# ───────────────────────────────────────────────────────────────────

def quiescence(board, alpha, beta, depth=5):
    stand_pat = evaluate(board)
    if stand_pat >= beta: return beta
    if stand_pat > alpha: alpha = stand_pat
    if depth == 0:        return alpha
    if stand_pat + 975 < alpha: return alpha   # delta pruning

    for move in board.legal_moves:
        if not board.is_capture(move) and not move.promotion:
            continue
        # SEE pruning: skip captures that clearly lose material
        if not move.promotion and see(board, move) < -50:
            continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha, depth - 1)
        board.pop()
        if score >= beta: return beta
        if score > alpha: alpha = score
    return alpha


# ───────────────────────────────────────────────────────────────────
#  FUTILITY PRUNING MARGINS
#
#  At depth 1: if eval + 200 <= alpha, skip quiet moves (minor piece can't help)
#  At depth 2: if eval + 500 <= alpha, skip quiet moves (rook can't help)
# ───────────────────────────────────────────────────────────────────
FUTILITY_MARGIN = {1: 200, 2: 500}


# ───────────────────────────────────────────────────────────────────
#  PVS  —  Principal Variation Search
# ───────────────────────────────────────────────────────────────────

def pvs(board, depth, alpha, beta, ply, start_time, time_limit, null_ok=True):

    if time.time() - start_time > time_limit:
        return evaluate(board)

    # ── Draw detection (smart contempt) ──
    if board.is_repetition(2) or board.is_fifty_moves():
        return draw_score(board)

    alpha_orig = alpha

    # ── Transposition table ──
    key = chess.polyglot.zobrist_hash(board)
    tt_score, tt_move = tt_probe(key, depth, alpha, beta)
    if tt_score is not None:
        return tt_score

    if depth <= 0 or board.is_game_over():
        return quiescence(board, alpha, beta)

    in_check = board.is_check()
    if in_check:
        depth += 1   # check extension

    # ── Razoring ──
    # At very shallow depth, if static eval is way below alpha,
    # there is no hope — drop straight to quiescence search.
    # Depth 1 margin = 200 (minor piece), Depth 2 margin = 400 (rook-ish)
    if not in_check and depth <= 2 and not (alpha < -90_000):
        razor_margin = 200 if depth == 1 else 400
        r_eval = evaluate(board)
        if r_eval + razor_margin < alpha:
            if depth == 1:
                return quiescence(board, alpha, beta)
            # depth 2: verify with QS before pruning
            qs = quiescence(board, alpha - razor_margin, alpha - razor_margin + 1)
            if qs + razor_margin < alpha:
                return qs

    # ── Null move pruning ──
    has_pieces = (board.pieces(chess.QUEEN, board.turn) |
                  board.pieces(chess.ROOK,  board.turn) |
                  board.pieces(chess.BISHOP,board.turn) |
                  board.pieces(chess.KNIGHT,board.turn))
    if null_ok and not in_check and depth >= 3 and has_pieces:
        R = 3 if depth >= 6 else 2
        board.push(chess.Move.null())
        null_score = -pvs(board, depth-1-R, -beta, -beta+1,
                          ply+1, start_time, time_limit, False)
        board.pop()
        if null_score >= beta:
            return beta

    # ── IID — Internal Iterative Deepening ──
    # If we have no TT move to guide ordering (TT miss), do a quick
    # shallow search first to find the best candidate move.
    # Only worth it at depth >= 5 where ordering really matters.
    if tt_move is None and depth >= 5 and not in_check:
        pvs(board, depth - 2, alpha, beta, ply, start_time, time_limit, False)
        # TT will now have a move hint from the shallow search
        _, tt_move = tt_probe(key, 0, alpha, beta)

    # ── Futility pruning (depth 1 & 2, not in check) ──
    futility_ok = False
    if not in_check and depth in FUTILITY_MARGIN:
        static_eval = evaluate(board)
        if static_eval + FUTILITY_MARGIN[depth] <= alpha:
            futility_ok = True

    # ── Main move loop ──
    best_move  = None
    best_score = -200_000
    moves_done = 0
    move_list  = ordered_moves(board, tt_move, ply)

    for move in move_list:
        if time.time() - start_time > time_limit:
            break

        is_cap    = board.is_capture(move)
        gives_chk = board.gives_check(move)

    # ── Futility pruning ──
        if futility_ok and not is_cap and not gives_chk and not move.promotion:
            continue

    # ── SEE pruning ──
        if is_cap and depth <= 3 and not in_check and see(board, move) < -100:
            continue

    # ✅ PUSH ONLY ONCE
        board.push(move)

    # ✅ Repetition avoidance (correct place)
        if board.is_repetition(2):
            board.pop()
            continue

    # ── Singular Extension ──
        singular_ext = 0
        if (move == tt_move and tt_move is not None
                and depth >= 6 and ply > 1
                and not in_check
                and _tt_flag[key & TT_MASK] == TT_EXACT
                and _tt_depth[key & TT_MASK] >= depth - 3):

            sing_beta  = _tt_score[key & TT_MASK] - 50
            sing_score = -200_000

            for other in move_list:
                other == tt_move:
                continue
                board.push(other)
                s = -pvs(board, depth-3, -sing_beta-1, -sing_beta,
                     ply+1, start_time, time_limit, False)
                board.pop()

                if s > sing_score:
                    sing_score = s
                if sing_score >= sing_beta:
                    break

            if sing_score < sing_beta:
                singular_ext = 1

    # ── PVS ──
        if moves_done == 0:
            score = -pvs(board, depth-1+singular_ext, -beta, -alpha,
                     ply+1, start_time, time_limit)
        else:
            score = -pvs(board, depth-1+singular_ext, -alpha-1, -alpha,
                        ply+1, start_time, time_limit)

    # ✅ ALWAYS pop once
        board.pop()

        # ── PVS ──
        ext = singular_ext
        if moves_done == 0:
            score = -pvs(board, depth-1+ext, -beta, -alpha,
                         ply+1, start_time, time_limit)
        else:
            reduction = 0
            if (depth >= 3 and moves_done >= 4 and not in_check
                    and not gives_chk and not is_cap and not move.promotion):
                reduction = 1 + (moves_done >= 8) + (depth >= 6 and moves_done >= 12)

            score = -pvs(board, depth-1-reduction+ext, -alpha-1, -alpha,
                         ply+1, start_time, time_limit)

            if reduction and score > alpha:
                score = -pvs(board, depth-1+ext, -alpha-1, -alpha,
                             ply+1, start_time, time_limit)

            if score > alpha and score < beta:
                score = -pvs(board, depth-1+ext, -beta, -alpha,
                             ply+1, start_time, time_limit)

        board.pop()
        moves_done += 1

        if score > best_score:
            best_score = score
            best_move  = move

        if score > alpha:
            alpha = score
            if not is_cap:
                update_history(move, depth)

        if alpha >= beta:
            if not is_cap:
                store_killer(move, ply)
            break

    if best_move is None:
        return evaluate(board)

    flag = TT_EXACT
    if best_score <= alpha_orig: flag = TT_UPPER
    elif best_score >= beta:     flag = TT_LOWER
    tt_store(key, depth, flag, best_score, best_move)

    return best_score


# ───────────────────────────────────────────────────────────────────
#  ITERATIVE DEEPENING ROOT
# ───────────────────────────────────────────────────────────────────

def _next_move(fen: str) -> str:
    global killers, history

    board = chess.Board(fen)
    moves = list(board.legal_moves)

    if not moves: return ""
    if len(moves) == 1: return moves[0].uci()

    killers  = [[None, None] for _ in range(MAX_DEPTH + 2)]
    history  = [[0] * 64 for _ in range(64)]

    TIME_LIMIT = 3.6
    start      = time.time()
    best_move  = moves[0]
    best_val   = -200_000
    prev_time  = 0.0

    for depth in range(1, MAX_DEPTH + 1):
        elapsed = time.time() - start
        if elapsed > TIME_LIMIT * 0.80:
            break
        if depth > 3 and prev_time * 4 > TIME_LIMIT - elapsed:
            break

        depth_start      = time.time()
        current_best     = None
        current_best_val = -200_000

        delta = 50
        if depth >= 3 and -80_000 < best_val < 80_000:
            asp_lo, asp_hi = best_val - delta, best_val + delta
        else:
            asp_lo, asp_hi = -200_000, 200_000

        for move in ordered_moves(board, None, 0):
            if time.time() - start > TIME_LIMIT:
                break

            board.push(move)
            val = -pvs(board, depth-1, -asp_hi, -asp_lo, 1, start, TIME_LIMIT)
            board.pop()

            if val <= asp_lo or val >= asp_hi:
                board.push(move)
                val = -pvs(board, depth-1, -200_000, 200_000, 1, start, TIME_LIMIT)
                board.pop()

            if val > current_best_val:
                current_best_val = val
                current_best     = move

        if current_best and time.time() - start <= TIME_LIMIT:
            best_move = current_best
            best_val  = current_best_val
            prev_time = time.time() - depth_start
            if best_val >= 90_000:
                break   # forced mate found

    return best_move.uci()


# ───────────────────────────────────────────────────────────────────
#  STALEMATE SAFETY WRAPPER
#  Final sanity check: never return a move that stalemated the opponent
#  unless it's literally the only legal move (forced stalemate = draw
#  is better than losing, but we should never cause it accidentally)
# ───────────────────────────────────────────────────────────────────

def _causes_stalemate(board, move):
    """Returns True if this move would stalemate the opponent."""
    board.push(move)
    result = board.is_stalemate()
    board.pop()
    return result


def next_move(fen: str) -> str:
    """Arena entry point — wraps _next_move with stalemate safety."""
    board  = chess.Board(fen)
    moves  = list(board.legal_moves)
    if not moves:
        return ""

    raw = _next_move(fen)
    chosen = chess.Move.from_uci(raw)

    # If the chosen move stalemated the opponent, pick the best
    # non-stalemate alternative
    if _causes_stalemate(board, chosen):
        safe_moves = [m for m in moves if not _causes_stalemate(board, m)]
        if safe_moves:
            # Pick the safe move with the best quick eval
            def quick_score(m):
                board.push(m)
                s = evaluate(board)
                board.pop()
                return s
            chosen = max(safe_moves, key=quick_score)

    return chosen.uci()


# ───────────────────────────────────────────────────────────────────
#  LOCAL TESTS
# ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("Starting pos",    chess.STARTING_FEN),
        ("Mate in 1",       "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"),
        ("Sicilian",        "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"),
        ("Endgame K+P",     "8/8/8/8/8/2K5/4P3/7k w - - 0 1"),
        ("Middlegame",      "r1bq1rk1/pp2ppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQ - 0 9"),
        ("Endgame passed",  "8/8/1k6/8/8/1K6/1P6/8 w - - 0 1"),
    ]

    print(f"\n{'Position':<32} {'Move':<8} {'Time':>6}  Notes")
    print("─" * 62)
    for name, fen in tests:
        t0 = time.time()
        m  = next_move(fen)
        elapsed = time.time() - t0
        b  = chess.Board(fen)
        ok = chess.Move.from_uci(m) in b.legal_moves
        b.push(chess.Move.from_uci(m))
        note = ""
        if b.is_checkmate():  note = "CHECKMATE!"
        if b.is_stalemate():  note = "STALEMATE!"
        if not ok:            note = "ILLEGAL!"
        print(f"{name:<32} {m:<8} {elapsed:>5.2f}s  {note}")
