import time
import chess

try:
    from chess.polyglot import zobrist_hash
except Exception:
    # Fallback, slower but safe.
    def zobrist_hash(board):
        return hash(board.fen())


# ---------------- CONFIG ---------------- #

PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

MATE_SCORE = 100000
INF = 10**9
TIME_LIMIT = 3.2  # stay comfortably under 5 seconds

# Endgame / repetition tuning
REPETITION_MARGIN = 220
REPETITION_WIN_PENALTY = 20000
REPETITION_LOSS_BONUS = 12000

# Anti-shuffling heuristic (replaces historical 3-fold)
HALFMOVE_CLOCK_PENALTY = 5

# Simplification bias in low-material positions.
ENDGAME_PHASE_THRESHOLD = 0.42
SIMPLIFY_BONUS = 14

# Move ordering weights
CHECK_BONUS = 60000
PROMOTION_BONUS = 90000
CAPTURE_BASE = 100000
TT_MOVE_BONUS = 10**9

# Transposition table flags
TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2
TT = {}


# ---------------- SMALL HELPERS ---------------- #

def ply_count(board):
    return 2 * (board.fullmove_number - 1) + (0 if board.turn == chess.WHITE else 1)


def center_bonus(square):
    f = chess.square_file(square)
    r = chess.square_rank(square)
    return 14 - 2 * (abs(f - 3) + abs(r - 3))


def king_ring(square):
    f = chess.square_file(square)
    r = chess.square_rank(square)
    squares = []
    for df in (-1, 0, 1):
        for dr in (-1, 0, 1):
            if df == 0 and dr == 0:
                continue
            nf = f + df
            nr = r + dr
            if 0 <= nf < 8 and 0 <= nr < 8:
                squares.append(chess.square(nf, nr))
    return squares


def is_passed_pawn(board, square, color, enemy_pawn_squares):
    f = chess.square_file(square)
    r = chess.square_rank(square)
    files = range(max(0, f - 1), min(7, f + 1) + 1)

    if color == chess.WHITE:
        for nf in files:
            for nr in range(r + 1, 8):
                if chess.square(nf, nr) in enemy_pawn_squares:
                    return False
    else:
        for nf in files:
            for nr in range(0, r):
                if chess.square(nf, nr) in enemy_pawn_squares:
                    return False
    return True


def pawn_supported(board, square, color):
    f = chess.square_file(square)
    r = chess.square_rank(square)
    support_rank = r - 1 if color == chess.WHITE else r + 1

    if not (0 <= support_rank < 8):
        return False

    for df in (-1, 1):
        nf = f + df
        if 0 <= nf < 8:
            sq = chess.square(nf, support_rank)
            piece = board.piece_at(sq)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                return True
    return False


def king_shield(board, square, color):
    f = chess.square_file(square)
    r = chess.square_rank(square)
    shield_rank = r + 1 if color == chess.WHITE else r - 1
    if not (0 <= shield_rank < 8):
        return 0

    shield = 0
    for df in (-1, 0, 1):
        nf = f + df
        if 0 <= nf < 8:
            sq = chess.square(nf, shield_rank)
            piece = board.piece_at(sq)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                shield += 1
    return shield


def material_balance_white(board):
    score = 0
    for piece in board.piece_map().values():
        val = PIECE_VALUE[piece.piece_type]
        score += val if piece.color == chess.WHITE else -val
    return score


def total_nonpawn_material(board):
    total = 0
    for piece in board.piece_map().values():
        if piece.piece_type != chess.PAWN and piece.piece_type != chess.KING:
            total += PIECE_VALUE[piece.piece_type]
    return total


def phase_of_game(board):
    # 1.0 = heavy material on board, 0.0 = sparse board.
    return min(1.0, total_nonpawn_material(board) / 5940.0)


def is_winning_white(board):
    return material_balance_white(board) > REPETITION_MARGIN


def is_losing_white(board):
    return material_balance_white(board) < -REPETITION_MARGIN


def is_mate_score(score):
    return abs(score) >= MATE_SCORE - 5000


# ---------------- EVALUATION ---------------- #

def repetition_score_white(board):
    """
    White-perspective score for claimable threefold repetition.
    Winning side should hate repetition.
    Losing side should welcome it.
    """
    if not board.can_claim_threefold_repetition():
        return 0

    material = material_balance_white(board)
    if material > REPETITION_MARGIN:
        return -(REPETITION_WIN_PENALTY + min(material // 4, 5000))
    if material < -REPETITION_MARGIN:
        return REPETITION_LOSS_BONUS + min((-material) // 4, 5000)
    return 0


def evaluate_white(board):
    # Terminal states first.
    if board.is_checkmate():
        # Side to move is mated.
        return -MATE_SCORE + ply_count(board) if board.turn == chess.WHITE else MATE_SCORE - ply_count(board)

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0

    # If repetition is claimable (within the current search tree), score it.
    if board.can_claim_threefold_repetition():
        return repetition_score_white(board)

    score = 0

    white_nonpawn = 0
    black_nonpawn = 0

    white_pawn_files = [0] * 8
    black_pawn_files = [0] * 8
    white_pawn_squares = set()
    black_pawn_squares = set()

    white_king = None
    black_king = None

    piece_map = board.piece_map()
    endgame = total_nonpawn_material(board) < 2600

    # First pass: material, piece activity, pawn bookkeeping.
    for square, piece in piece_map.items():
        color = piece.color
        sign = 1 if color == chess.WHITE else -1
        ptype = piece.piece_type
        val = PIECE_VALUE[ptype]

        score += sign * val

        if ptype != chess.PAWN and ptype != chess.KING:
            if color == chess.WHITE:
                white_nonpawn += val
            else:
                black_nonpawn += val

        if ptype == chess.KING:
            if color == chess.WHITE:
                white_king = square
            else:
                black_king = square

        if ptype == chess.PAWN:
            file = chess.square_file(square)
            if color == chess.WHITE:
                white_pawn_files[file] += 1
                white_pawn_squares.add(square)
            else:
                black_pawn_files[file] += 1
                black_pawn_squares.add(square)

        # Piece-square style centrality and activity.
        if ptype == chess.KNIGHT:
            score += sign * (center_bonus(square) * 10)
            if board.is_pinned(color, square):
                score -= sign * 25
        elif ptype == chess.BISHOP:
            score += sign * (center_bonus(square) * 5)
            if board.is_pinned(color, square):
                score -= sign * 20
        elif ptype == chess.ROOK:
            score += sign * (center_bonus(square) * 2)
            if board.is_pinned(color, square):
                score -= sign * 15
        elif ptype == chess.QUEEN:
            score += sign * (center_bonus(square) * 2)
            if board.is_pinned(color, square):
                score -= sign * 12
        elif ptype == chess.PAWN:
            rank = chess.square_rank(square)
            advancement = rank if color == chess.WHITE else 7 - rank
            score += sign * (advancement * 6)

            file = chess.square_file(square)
            same_file_count = white_pawn_files[file] if color == chess.WHITE else black_pawn_files[file]
            if same_file_count > 1:
                score -= sign * (12 * (same_file_count - 1))

            left = (white_pawn_files if color == chess.WHITE else black_pawn_files)[file - 1] if file > 0 else 0
            right = (white_pawn_files if color == chess.WHITE else black_pawn_files)[file + 1] if file < 7 else 0
            if left == 0 and right == 0:
                score -= sign * 10

            enemy_pawns = black_pawn_squares if color == chess.WHITE else white_pawn_squares
            if is_passed_pawn(board, square, color, enemy_pawns):
                passed_bonus = 20 + advancement * (10 if endgame else 6)
                score += sign * passed_bonus
                if pawn_supported(board, square, color):
                    score += sign * 12
                if endgame:
                    score += sign * (advancement * 4)

        # Mobility.
        if ptype in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
            mobility = len(board.attacks(square))
            if board.is_pinned(color, square):
                mobility = max(0, mobility - 2)

            if ptype == chess.KNIGHT:
                score += sign * (mobility * 5)
            elif ptype == chess.BISHOP:
                score += sign * (mobility * 4)
            elif ptype == chess.ROOK:
                score += sign * (mobility * 2)
            elif ptype == chess.QUEEN:
                score += sign * (mobility * 1)

        # Rooks love open files and the 7th rank.
        if ptype == chess.ROOK:
            file = chess.square_file(square)
            own_pawns = white_pawn_files[file] if color == chess.WHITE else black_pawn_files[file]
            opp_pawns = black_pawn_files[file] if color == chess.WHITE else white_pawn_files[file]

            if own_pawns == 0 and opp_pawns == 0:
                score += sign * 20
            elif own_pawns == 0 and opp_pawns > 0:
                score += sign * 10

            rank = chess.square_rank(square)
            if (color == chess.WHITE and rank == 6) or (color == chess.BLACK and rank == 1):
                score += sign * 18

    # Bishop pair.
    if sum(1 for p in piece_map.values() if p.color == chess.WHITE and p.piece_type == chess.BISHOP) >= 2:
        score += 30
    if sum(1 for p in piece_map.values() if p.color == chess.BLACK and p.piece_type == chess.BISHOP) >= 2:
        score -= 30

    # King safety and activity.
    if white_king is not None:
        if endgame:
            score += center_bonus(white_king) * 8
        else:
            danger = 0
            for sq in king_ring(white_king):
                danger += len(board.attackers(chess.BLACK, sq))
            shield = king_shield(board, white_king, chess.WHITE)
            score += shield * 10
            score -= danger * 16

    if black_king is not None:
        if endgame:
            score -= center_bonus(black_king) * 8
        else:
            danger = 0
            for sq in king_ring(black_king):
                danger += len(board.attackers(chess.WHITE, sq))
            shield = king_shield(board, black_king, chess.BLACK)
            score -= shield * 10
            score += danger * 16

    # Simplification bias only in cleaner endgames.
    phase = phase_of_game(board)
    material_diff = material_balance_white(board)
    if phase < ENDGAME_PHASE_THRESHOLD:
        if material_diff > 300:
            score -= SIMPLIFY_BONUS
        elif material_diff < -300:
            score += SIMPLIFY_BONUS

    # ---------------------------------------------------------
    # NEW: Anti-Shuffling Heuristic
    # ---------------------------------------------------------
    # Penalize/reward high halfmove clocks to force progress or stall.
    if score > REPETITION_MARGIN:
        score -= board.halfmove_clock * HALFMOVE_CLOCK_PENALTY
    elif score < -REPETITION_MARGIN:
        score += board.halfmove_clock * HALFMOVE_CLOCK_PENALTY

    return score


def evaluate(board):
    white_score = evaluate_white(board)
    return white_score if board.turn == chess.WHITE else -white_score


# ---------------- MOVE ORDERING ---------------- #

def move_order_score(board, move, tt_move=None):
    score = 0

    if tt_move is not None and move == tt_move:
        return TT_MOVE_BONUS

    tactical = False

    # Promotions are force multipliers.
    if move.promotion:
        tactical = True
        score += PROMOTION_BONUS + PIECE_VALUE[move.promotion]

    # Checks are king-hunting breadcrumbs.
    if board.gives_check(move):
        tactical = True
        score += CHECK_BONUS

    # Captures: MVV-LVA style, but keep the weight moderate so search can do the real thinking.
    if board.is_capture(move):
        tactical = True
        if board.is_en_passant(move):
            captured_value = PIECE_VALUE[chess.PAWN]
        else:
            victim = board.piece_at(move.to_square)
            captured_value = PIECE_VALUE[victim.piece_type] if victim else 0

        attacker = board.piece_at(move.from_square)
        attacker_value = PIECE_VALUE[attacker.piece_type] if attacker else 0

        score += CAPTURE_BASE + (captured_value * 20) - (attacker_value * 2)

        # In a clearly winning endgame, trading is nice, but only after tactical priorities.
        if phase_of_game(board) < ENDGAME_PHASE_THRESHOLD:
            mat = material_balance_white(board)
            if board.turn == chess.BLACK:
                mat = -mat
            if mat > REPETITION_MARGIN and captured_value >= attacker_value:
                score += 1200

    # Quiet centralization still matters a bit.
    score += center_bonus(move.to_square) * 2

    # Prefer forcing moves over quiet ones, but never overrule a tactical knockout.
    if tactical:
        score += 1000

    return score


def ordered_moves(board, tt_move=None):
    moves = list(board.legal_moves)
    moves.sort(key=lambda mv: move_order_score(board, mv, tt_move), reverse=True)
    return moves


# ---------------- SEARCH ---------------- #

def quiescence(board, alpha, beta, deadline):
    if time.perf_counter() >= deadline:
        raise TimeoutError

    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    forcing = []
    for move in board.legal_moves:
        if board.is_capture(move) or move.promotion or board.gives_check(move):
            forcing.append(move)

    forcing.sort(key=lambda mv: move_order_score(board, mv), reverse=True)

    for move in forcing:
        board.push(move)
        score = -quiescence(board, -beta, -alpha, deadline)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def search_extension(board, move):
    # Light tactical extension only.
    # IMPORTANT: this must be evaluated on the current board position,
    # before the move is pushed. The move is pseudo-legal here, but not
    # after the board has advanced.
    ext = 0
    if board.gives_check(move):
        ext += 1
    if move.promotion:
        ext += 1
    if board.is_capture(move):
        victim = None
        if not board.is_en_passant(move):
            victim = board.piece_at(move.to_square)
        if board.is_en_passant(move) or (victim and victim.piece_type in (chess.QUEEN, chess.ROOK)):
            ext += 1
    return min(ext, 1)


def negamax(board, depth, alpha, beta, deadline):
    if time.perf_counter() >= deadline:
        raise TimeoutError

    key = zobrist_hash(board)
    entry = TT.get(key)
    tt_move = None

    if entry is not None:
        entry_depth, entry_flag, entry_value, entry_best_move = entry
        tt_move = entry_best_move

        if entry_depth >= depth:
            if entry_flag == TT_EXACT:
                return entry_value
            elif entry_flag == TT_LOWER:
                alpha = max(alpha, entry_value)
            elif entry_flag == TT_UPPER:
                beta = min(beta, entry_value)

            if alpha >= beta:
                return entry_value

    if depth <= 0:
        return quiescence(board, alpha, beta, deadline)

    if board.is_checkmate():
        return -MATE_SCORE + ply_count(board)

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0

    # Do not stop search on threefold here.
    # Let the engine keep looking for mate or a stronger conversion line.

    best_value = -INF
    best_move = None
    alpha_orig = alpha

    moves = ordered_moves(board, tt_move=tt_move)
    if not moves:
        return evaluate(board)

    for move in moves:
        child_extension = search_extension(board, move)
        board.push(move)
        child_depth = depth - 1 + child_extension
        score = -negamax(board, child_depth, -beta, -alpha, deadline)
        board.pop()

        if score > best_value:
            best_value = score
            best_move = move

        if score > alpha:
            alpha = score

        if alpha >= beta:
            break

    flag = TT_EXACT
    if best_value <= alpha_orig:
        flag = TT_UPPER
    elif best_value >= beta:
        flag = TT_LOWER

    TT[key] = (depth, flag, best_value, best_move)
    return best_value


# ---------------- ROOT HELPERS ---------------- #

def find_immediate_mate(board):
    for move in ordered_moves(board):
        board.push(move)
        mate = board.is_checkmate()
        board.pop()
        if mate:
            return move
    return None


def root_search(board, depth, deadline):
    root_tt_move = TT.get(zobrist_hash(board), (None, None, None, None))[3] if zobrist_hash(board) in TT else None
    root_moves = ordered_moves(board, tt_move=root_tt_move)

    best_move = None
    best_score = -INF
    alpha = -INF
    beta = INF

    for move in root_moves:
        child_extension = search_extension(board, move)
        board.push(move)
        child_depth = depth - 1 + child_extension
        score = -negamax(board, child_depth, -beta, -alpha, deadline)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

        if score > alpha:
            alpha = score

        # If we have a proven mate line, take it immediately.
        if is_mate_score(score):
            return move, score

    return best_move, best_score


# ---------------- MAIN MOVE ---------------- #

def next_move(fen):
    board = chess.Board(fen)
    deadline = time.perf_counter() + TIME_LIMIT

    legal = list(board.legal_moves)
    if not legal:
        return None

    # Absolute mate-in-1 check: cheap, safe, and decisive.
    mate1 = find_immediate_mate(board)
    if mate1 is not None:
        return str(mate1)

    best_move = legal[0]
    depth = 1

    try:
        while True:
            move, score = root_search(board, depth, deadline)
            if move is not None:
                best_move = move

            # Once a forced mate is found, keep it.
            if is_mate_score(score):
                return str(best_move)

            depth += 1

    except TimeoutError:
        pass

    if best_move is None:
        best_move = legal[0]

    return str(best_move)