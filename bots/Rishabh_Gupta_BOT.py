import chess
import time

# Piece values
PIECE_VALUE = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}


def evaluate_board(board):
    """Simple and fast board evaluation"""
    if board.is_checkmate():
        return 10000 if board.turn == chess.BLACK else -10000
    
    if board.is_stalemate():
        return 0
    
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUE[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    
    return score


def minimax(board, depth, alpha, beta, is_maximizing, start_time):
    """Alpha-beta minimax with depth limit"""
    
    # Time limit check (every 2 levels)
    if depth % 2 == 0 and time.time() - start_time > 3.5:
        return evaluate_board(board)
    
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    legal_moves = list(board.legal_moves)
    
    if not legal_moves:
        return evaluate_board(board)
    
    if is_maximizing:
        max_eval = -float('inf')
        
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False, start_time)
            board.pop()
            
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            
            if beta <= alpha:
                break
        
        return max_eval
    
    else:
        min_eval = float('inf')
        
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True, start_time)
            board.pop()
            
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            
            if beta <= alpha:
                break
        
        return min_eval


def order_moves(board):
    """Order moves: captures first, then checks, then quiet"""
    moves = list(board.legal_moves)
    
    captures = []
    checks = []
    quiet = []
    
    for move in moves:
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            captures.append((PIECE_VALUE.get(captured_piece.piece_type, 0), move))
        elif board.gives_check(move):
            checks.append(move)
        else:
            quiet.append(move)
    
    # Sort captures by piece value (highest first)
    captures.sort(reverse=True, key=lambda x: x[0])
    
    return [m[1] for m in captures] + checks + quiet


def next_move(fen):
    """Find best move using alpha-beta pruning"""
    board = chess.Board(fen)
    legal_moves = list(board.legal_moves)
    
    if not legal_moves:
        return None
    
    if len(legal_moves) == 1:
        return str(legal_moves[0])
    
    # Check for immediate checkmate
    for move in legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return str(move)
        board.pop()
    
    start_time = time.time()
    
    # Adjust depth based on number of moves
    num_moves = len(legal_moves)
    if num_moves > 35:
        depth = 2
    elif num_moves > 20:
        depth = 3
    elif num_moves > 10:
        depth = 4
    else:
        depth = 5
    
    best_move = None
    best_score = -float('inf') if board.turn == chess.WHITE else float('inf')
    
    ordered_moves = order_moves(board)
    
    for move in ordered_moves:
        board.push(move)
        
        is_max = board.turn == chess.BLACK
        score = minimax(board, depth - 1, -float('inf'), float('inf'), is_max, start_time)
        
        board.pop()
        
        if board.turn == chess.WHITE:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move
        
        # Time check
        if time.time() - start_time > 3.7:
            break
    
    return str(best_move) if best_move else str(legal_moves[0])
