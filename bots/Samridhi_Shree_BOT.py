
import chess
import random


piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def evaluate_board(board):
    
    if board.is_checkmate():
        return -99999 
        
    
    if board.can_claim_threefold_repetition():
        return -50000 
        
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0 

    score = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            
           
            if piece.piece_type in [chess.KNIGHT, chess.PAWN]:
                if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                    value += 30
                elif square in [chess.C3, chess.F3, chess.C6, chess.F6, chess.C4, chess.F4, chess.C5, chess.F5]:
                    value += 10
            
            
            elif piece.piece_type == chess.BISHOP:
                if piece.color == chess.WHITE and chess.square_rank(square) > 0:
                    value += 15
                elif piece.color == chess.BLACK and chess.square_rank(square) < 7:
                    value += 15

            
            elif piece.piece_type == chess.QUEEN:
                if square in [chess.D4, chess.E4, chess.D5, chess.E5, chess.C3, chess.F3, chess.C6, chess.F6]:
                    value -= 15 

            
            elif piece.piece_type == chess.KING:
                if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                    value -= 50

            
            if piece.color == board.turn:
                score += value
            else:
                score -= value
                
    return score

def order_moves(board, moves):
    
    return sorted(moves, key=lambda m: board.is_capture(m), reverse=True)

def negamax(board, depth, alpha, beta):
    
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    max_score = -float('inf')
    moves = order_moves(board, list(board.legal_moves))
    
    for move in moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if score > max_score:
            max_score = score
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break 
            
    return max_score

def next_move(fen):
    
    board = chess.Board(fen)
    best_move = None
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')

    
    DEPTH = 3 

    moves = list(board.legal_moves)
    if not moves:
        return ""
        
    moves = order_moves(board, moves)

    for move in moves:
        board.push(move)
        score = -negamax(board, DEPTH - 1, -beta, -alpha)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    # Fallback safety net
    if best_move is None:
        best_move = random.choice(moves)

    return best_move.uci()
