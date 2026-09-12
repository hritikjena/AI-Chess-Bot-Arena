import chess
import time

# =========================
# GLOBALS
# =========================

transposition_table = {}
killer_moves = {}

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# =========================
# EVALUATION
# =========================

def evaluate(board):
    if board.is_checkmate():
        return -100000 if board.turn else 100000

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

    # Mobility
    score += len(list(board.legal_moves)) * 2

    return score


# =========================
# MOVE ORDERING (STRONG)
# =========================

def move_score(board, move, depth):
    score = 0

    # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            score += 10 * piece_values[victim.piece_type] - piece_values[attacker.piece_type]

    # Promotions
    if move.promotion:
        score += 900

    # Killer move
    if depth in killer_moves and move in killer_moves[depth]:
        score += 800

    # Check bonus
    board.push(move)
    if board.is_check():
        score += 500
    board.pop()

    return score


def order_moves(board, depth):
    return sorted(board.legal_moves, key=lambda m: move_score(board, m, depth), reverse=True)


# =========================
# QUIESCENCE SEARCH
# =========================

def quiescence(board, alpha, beta):
    stand_pat = evaluate(board)

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if not board.is_capture(move):
            continue

        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# =========================
# MINIMAX (NEGAMAX STYLE)
# =========================

def minimax(board, depth, alpha, beta, start_time, time_limit):
    key = (board.fen(), depth)

    if key in transposition_table:
        return transposition_table[key]

    # Time cutoff
    if time.time() - start_time > time_limit:
        return evaluate(board)

    if depth == 0:
        return quiescence(board, alpha, beta)

    if board.is_game_over():
        return evaluate(board)

    max_eval = -1000000

    for move in order_moves(board, depth):
        board.push(move)

        # Check extension
        extension = 1 if board.is_check() else 0

        eval = -minimax(
            board,
            depth - 1 + extension,
            -beta,
            -alpha,
            start_time,
            time_limit
        )

        board.pop()

        if eval > max_eval:
            max_eval = eval

        if eval > alpha:
            alpha = eval

        if alpha >= beta:
            # Store killer move
            if depth not in killer_moves:
                killer_moves[depth] = []
            killer_moves[depth].append(move)
            break

    transposition_table[key] = max_eval
    return max_eval


# =========================
# MAIN FUNCTION
# =========================

def next_move(fen):
    board = chess.Board(fen)

    start_time = time.time()
    time_limit = 3.8

    best_move = None
    depth = 1

    while True:
        if time.time() - start_time > time_limit:
            break

        best_value = -1000000
        current_best = None

        for move in order_moves(board, depth):
            board.push(move)

            value = -minimax(
                board,
                depth - 1,
                -1000000,
                1000000,
                start_time,
                time_limit
            )

            board.pop()

            if value > best_value:
                best_value = value
                current_best = move

        if current_best:
            best_move = current_best

        depth += 1

    return str(best_move)