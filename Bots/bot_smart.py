import chess

piece_value = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# ---------------- EVALUATION ---------------- #

def evaluate(board):

    # 🔥 checkmate = biggest priority
    if board.is_checkmate():
        if board.turn:
            return -10000
        else:
            return 10000

    # draw = neutral
    if (board.is_stalemate() or 
        board.is_insufficient_material() or 
        board.can_claim_fifty_moves() or 
        board.can_claim_threefold_repetition()):
        return 0

    score = 0

    # material count
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_value[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

    # 🔥 encourage giving check
    if board.is_check():
        score += 0.5 if board.turn == chess.BLACK else -0.5

    return score


# ---------------- MINIMAX ---------------- #

def minimax(board, depth, maximizing):

    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if maximizing:
        max_eval = -9999

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()

            max_eval = max(max_eval, eval)

        return max_eval

    else:
        min_eval = 9999

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()

            min_eval = min(min_eval, eval)

        return min_eval


# ---------------- MAIN MOVE ---------------- #

def next_move(fen):
    board = chess.Board(fen)

    best_move = None
    best_score = -9999 if board.turn == chess.WHITE else 9999

    for move in board.legal_moves:
        board.push(move)

        # 🔥 depth = 2 search
        score = minimax(board, 2, board.turn == chess.BLACK)

        board.pop()

        if board.turn == chess.WHITE:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    return str(best_move)