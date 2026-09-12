import chess
import time
import random
import math

MATE_SCORE = 100000
MATE_THRESHOLD = 90000
TIME_LIMIT = 3.6

# PeSTO's Evaluation parameters (scaled for speed)
MG_VALUE = [0, 82, 337, 365, 477, 1025, 0]
EG_VALUE = [0, 94, 281, 297, 512,  936, 0]

MG_PAWN = [
      0,   0,   0,   0,   0,   0,   0,   0,
     98, 134,  61,  95,  68, 126,  34, -11,
     -6,   7,  26,  31,  65,  56,  25, -20,
    -14,  13,   6,  21,  23,  12,  17, -23,
    -27,  -2,  -5,  12,  17,   6,  10, -25,
    -26,  -4,  -4, -10,   3,   3,  33, -12,
    -35,  -1, -20, -23, -15,  24,  38, -22,
      0,   0,   0,   0,   0,   0,   0,   0,
]
EG_PAWN = [
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0,
]

MG_KNIGHT = [
    -167, -89, -34, -49,  61, -97, -15, -107,
     -73, -41,  72,  36,  23,  62,   7,  -17,
     -47,  60,  37,  65,  84, 129,  73,   44,
      -9,  17,  19,  53,  37,  69,  18,   22,
     -13,   4,  16,  13,  28,  19,  21,   -8,
     -23,  -9,  12,  10,  19,  17,  25,  -16,
     -29, -53, -12,  -3,  -1,  18, -14,  -19,
    -105, -21, -58, -33, -17, -28, -19,  -23,
]
EG_KNIGHT = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64,
]

MG_BISHOP = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
]
EG_BISHOP = [
    -14, -21, -11,  -8, -7,  -9, -17, -24,
     -8,  -4,   7, -12, -3, -13,  -4, -14,
      2,  -8,   0,  -1, -2,   6,   0,   4,
     -3,   9,  12,   9, 14,  10,   3,   2,
     -6,   3,  13,  19,  7,  10,  -3,  -9,
    -12,  -3,   8,  10, 13,   3,  -7, -15,
    -14, -18,  -7,  -1,  4,  -9, -15, -27,
    -23,  -9, -23,  -5, -9, -16,  -5, -17,
]

MG_ROOK = [
     32,  42,  32,  51, 63,  9,  31,  43,
     27,  32,  58,  62, 80, 67,  26,  44,
     -5,  19,  26,  36, 17, 45,  61,  16,
    -24, -11,   7,  26, 24, 35,  -8, -20,
    -36, -26, -12,  -1,  9, -7,   6, -23,
    -45, -25, -16, -17,  3,  0,  -5, -33,
    -44, -16, -20,  -9, -1, 11,  -6, -71,
    -19, -13,   1,  17, 16,  7, -37, -26,
]
EG_ROOK = [
    13, 10, 18, 15, 12,  12,   8,   5,
    11, 13, 13, 11, -3,   3,   8,   3,
     7,  7,  7,  5,  4,  -3,  -5,  -3,
     4,  3, 13,  1,  2,   1,  -1,   2,
     3,  5,  8,  4, -5,  -6,  -8, -11,
    -4,  0, -5, -1, -7, -12,  -8, -16,
    -6, -6,  0,  2, -9,  -9, -11,  -3,
    -9,  2,  3, -1, -5, -13,   4, -20,
]

MG_QUEEN = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
]
EG_QUEEN = [
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  57,  40,  57,  36,
    -18,  28,  19,  47,  31,  34,  12,  11,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41,
]

MG_KING = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
]
EG_KING = [
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43,
]

def mirror_score(table):
    return [table[chess.square_mirror(sq)] for sq in range(64)]

MG_PST = [
    [], # None
    [MG_VALUE[1] + MG_PAWN[sq] for sq in range(64)],
    [MG_VALUE[2] + MG_KNIGHT[sq] for sq in range(64)],
    [MG_VALUE[3] + MG_BISHOP[sq] for sq in range(64)],
    [MG_VALUE[4] + MG_ROOK[sq] for sq in range(64)],
    [MG_VALUE[5] + MG_QUEEN[sq] for sq in range(64)],
    [MG_VALUE[6] + MG_KING[sq] for sq in range(64)]
]
EG_PST = [
    [], # None
    [EG_VALUE[1] + EG_PAWN[sq] for sq in range(64)],
    [EG_VALUE[2] + EG_KNIGHT[sq] for sq in range(64)],
    [EG_VALUE[3] + EG_BISHOP[sq] for sq in range(64)],
    [EG_VALUE[4] + EG_ROOK[sq] for sq in range(64)],
    [EG_VALUE[5] + EG_QUEEN[sq] for sq in range(64)],
    [EG_VALUE[6] + EG_KING[sq] for sq in range(64)]
]

MG_PST_BLACK = [
    [],
    [MG_VALUE[1] + mirror_score(MG_PAWN)[sq] for sq in range(64)],
    [MG_VALUE[2] + mirror_score(MG_KNIGHT)[sq] for sq in range(64)],
    [MG_VALUE[3] + mirror_score(MG_BISHOP)[sq] for sq in range(64)],
    [MG_VALUE[4] + mirror_score(MG_ROOK)[sq] for sq in range(64)],
    [MG_VALUE[5] + mirror_score(MG_QUEEN)[sq] for sq in range(64)],
    [MG_VALUE[6] + mirror_score(MG_KING)[sq] for sq in range(64)]
]
EG_PST_BLACK = [
    [],
    [EG_VALUE[1] + mirror_score(EG_PAWN)[sq] for sq in range(64)],
    [EG_VALUE[2] + mirror_score(EG_KNIGHT)[sq] for sq in range(64)],
    [EG_VALUE[3] + mirror_score(EG_BISHOP)[sq] for sq in range(64)],
    [EG_VALUE[4] + mirror_score(EG_ROOK)[sq] for sq in range(64)],
    [EG_VALUE[5] + mirror_score(EG_QUEEN)[sq] for sq in range(64)],
    [EG_VALUE[6] + mirror_score(EG_KING)[sq] for sq in range(64)]
]

game_phase_inc = [0, 0, 1, 1, 2, 4, 0]

OPENING_BOOK = {
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -': 'e2e4',
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3': 'c7c5',
    'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6': 'g1f3',
    'rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -': 'd7d6',
    'rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -': 'd2d4',
    'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3': 'g8f6',
    'rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq -': 'c2c4',
    'rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3': 'e7e6',
    'rnbqkb1r/pppp1ppp/4pn2/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -': 'g1f3',
    'rnbqkb1r/pppp1ppp/4pn2/8/2PP4/5N2/PP2PPPP/RNBQKB1R b KQkq -': 'd7d5',
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3': 'e7e5',
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6': 'g1f3',
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -': 'b8c6',
    'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -': 'f1b5',
    'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -': 'a7a6',
    'r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq -': 'b5a4',
    'r1bqkbnr/1ppp1ppp/p1n5/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R b KQkq -': 'g8f6',
    'r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R w KQkq -': 'e1g1',
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3': 'e7e6',
    'rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
    # Queen's Gambit
    'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3': 'd7d5',
    'rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6': 'c2c4',
    'rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3': 'e7e6',
    'rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -': 'b1c3',
    'rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq -': 'g8f6',
    # King's Indian
    'rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq -': 'g7g6',
    'rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -': 'b1c3',
    'rnbqkb1r/pppppp1p/5np1/8/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq -': 'f8g7',
    # Caro-Kann
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3': 'c7c6',
    'rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
    'rnbqkbnr/pp1ppppp/2p5/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3': 'd7d5',
    'rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6': 'e4d5',
    # French Defence
    'rnbqkbnr/pppp1ppp/4p3/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3': 'd7d5',
    'rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6': 'b1c3',
    # London System
    'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3': 'g8f6',
    'rnbqkb1r/pppppppp/5n2/8/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq -': 'd7d5',
    'rnbqkb1r/ppp1pppp/5n2/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R w KQkq -': 'c1f4',
    # Sicilian Najdorf continuation
    'rnbqkb1r/1p2pppp/p2p1n2/2p5/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq -': 'f1e2',
    # Ruy Lopez castle
    'r1bqk2r/1ppp1ppp/p1n2n2/1Bb1p3/B3P3/5N2/PPPP1PPP/RNBQK2R b KQkq -': 'e8g8',
    # English Opening
    'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3': 'e7e5',
    'rnbqkbnr/pppp1ppp/8/4p3/2P5/8/PP1PPPPP/RNBQKBNR w KQkq e6': 'b1c3',
}

def get_opening_move(board):
    fen_key = ' '.join(board.fen().split()[:4])
    return OPENING_BOOK.get(fen_key)

def evaluate(board):
    mg_score = 0
    eg_score = 0
    phase = 0

    for pt in range(1, 7):
        w_pieces = board.pieces(pt, chess.WHITE)
        b_pieces = board.pieces(pt, chess.BLACK)
        
        for sq in w_pieces:
            mg_score += MG_PST[pt][sq]
            eg_score += EG_PST[pt][sq]
        for sq in b_pieces:
            mg_score -= MG_PST_BLACK[pt][sq]
            eg_score -= EG_PST_BLACK[pt][sq]
            
        phase += game_phase_inc[pt] * (len(w_pieces) + len(b_pieces))

    phase = min(24, phase)
    mg_weight = phase
    eg_weight = 24 - phase

    score = (mg_score * mg_weight + eg_score * eg_weight) // 24
    
    return score if board.turn == chess.WHITE else -score

transposition_table = {}
killer_moves = [[None, None] for _ in range(128)]
history_table = []
search_start_time = 0
nodes_searched = 0
time_is_up = False

def check_time():
    global time_is_up
    if time.time() - search_start_time >= TIME_LIMIT:
        time_is_up = True

def order_moves(board, moves, ply, tt_move=None):
    scored_moves = []
    
    for move in moves:
        if move == tt_move:
            score = 10000000
        elif board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            v_val = victim.piece_type if victim else 0
            a_val = attacker.piece_type if attacker else 0
            score = 1000000 + v_val * 10 - a_val
            if move.promotion:
                score += 500000
        else:
            if move.promotion:
                score = 500000
            elif ply < len(killer_moves) and move in killer_moves[ply]:
                score = 900000 if move == killer_moves[ply][0] else 800000
            else:
                score = history_table[1 if board.turn else 0][move.from_square][move.to_square]
        scored_moves.append((score, move))
        
    scored_moves.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in scored_moves]

def quiescence(board, alpha, beta, ply):
    global nodes_searched, time_is_up
    nodes_searched += 1
    if nodes_searched & 511 == 0:
        check_time()
    if time_is_up:
        return 0
    
    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    moves = board.generate_pseudo_legal_captures()
    legal_caps = [m for m in moves if board.is_legal(m)]
    
    scored_moves = []
    for move in legal_caps:
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        v_val = victim.piece_type if victim else 0
        a_val = attacker.piece_type if attacker else 0
        score = v_val * 10 - a_val
        scored_moves.append((score, move))
    scored_moves.sort(key=lambda x: x[0], reverse=True)

    DELTA_VALUES = [0, 100, 320, 330, 500, 900, 20000]
    for _, move in scored_moves:
        if move.promotion:
            pass
        else:
            victim = board.piece_at(move.to_square)
            if victim and stand_pat + DELTA_VALUES[victim.piece_type] + 200 < alpha:
                continue  # skip this capture, can't improve alpha
            
        board.push(move)
        score = -quiescence(board, -beta, -alpha, ply + 1)
        board.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            
    return alpha

def negamax(board, depth, alpha, beta, ply, null_move_allowed):
    global nodes_searched, time_is_up
    nodes_searched += 1
    if nodes_searched & 511 == 0:
        check_time()
        
    if time_is_up:
        return (0, None) if ply == 0 else 0
        
    if ply > 0 and board.is_repetition(2):
        return 0

    if board.is_game_over():
        if board.is_checkmate():
            return (-MATE_SCORE + ply, None) if ply == 0 else -MATE_SCORE + ply
        return (0, None) if ply == 0 else 0
        
    if depth <= 0:
        score = quiescence(board, alpha, beta, ply)
        return (score, None) if ply == 0 else score

    alpha_orig = alpha
    tt_move = None
    
    tt_key = board._transposition_key()

    tt_entry = transposition_table.get(tt_key)
    if tt_entry and tt_entry['depth'] >= depth:
        tt_flag = tt_entry['flag']
        tt_score = tt_entry['score']
        if tt_flag == 'EXACT':
            return (tt_score, tt_entry['move']) if ply == 0 else tt_score
        elif tt_flag == 'LOWERBOUND':
            alpha = max(alpha, tt_score)
        elif tt_flag == 'UPPERBOUND':
            beta = min(beta, tt_score)
        if alpha >= beta:
            return (tt_score, tt_entry['move']) if ply == 0 else tt_score
        tt_move = tt_entry['move']

    in_check = board.is_check()
    
    if in_check:
        depth += 1
        
    if not in_check and depth >= 3 and null_move_allowed and ply > 0:
        has_pieces = False
        for pt in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            if board.pieces(pt, board.turn):
                has_pieces = True
                break
        if has_pieces:
            board.push(chess.Move.null())
            null_score = -negamax(board, depth - 3, -beta, -beta + 1, ply + 1, False)
            board.pop()
            if null_score >= beta:
                return beta
                
    FUTILITY_MARGIN = [0, 150, 300]
    if not in_check and abs(alpha) < 90000 and abs(beta) < 90000:
        static_eval = evaluate(board)
        # Reverse Futility Pruning
        if depth <= 3 and static_eval - 120 * depth >= beta:
            return static_eval
        # Futility Pruning
        if 1 <= depth <= 2 and static_eval + FUTILITY_MARGIN[depth] <= alpha:
            return quiescence(board, alpha, beta, ply)

    moves = list(board.legal_moves)
    ordered_moves = order_moves(board, moves, ply, tt_move)
    
    best_move = None
    best_score = -1000000

    for i, move in enumerate(ordered_moves):
        board.push(move)
        
        is_capture = board.is_capture(move)
        
        if i == 0:
            score = -negamax(board, depth - 1, -beta, -alpha, ply + 1, True)
        else:
            if depth >= 3 and not in_check and not is_capture and i >= 2:
                reduction = max(1, int(math.log(depth) * math.log(i + 1) / 2.0))
                reduction = min(reduction, depth - 2)
                score = -negamax(board, depth - 1 - reduction, -alpha - 1, -alpha, ply + 1, True)
                if score > alpha:
                    score = -negamax(board, depth - 1, -alpha - 1, -alpha, ply + 1, True)
            else:
                score = -negamax(board, depth - 1, -alpha - 1, -alpha, ply + 1, True)
                
            if alpha < score < beta:
                score = -negamax(board, depth - 1, -beta, -alpha, ply + 1, True)
                
        board.pop()
        
        if time_is_up:
            return (0, None) if ply == 0 else 0
            
        if score > best_score:
            best_score = score
            best_move = move
            
        if score > alpha:
            alpha = score
            
        if alpha >= beta:
            if not is_capture:
                if ply < 128:
                    if killer_moves[ply][0] != move:
                        killer_moves[ply][1] = killer_moves[ply][0]
                        killer_moves[ply][0] = move
                history_table[1 if board.turn else 0][move.from_square][move.to_square] += depth * depth
            break

    if time_is_up:
        return (0, None) if ply == 0 else 0

    if best_score <= alpha_orig:
        flag = 'UPPERBOUND'
    elif best_score >= beta:
        flag = 'LOWERBOUND'
    else:
        flag = 'EXACT'
        
    if len(transposition_table) < 2000000:
        transposition_table[tt_key] = {
            'depth': depth,
            'score': best_score,
            'flag': flag,
            'move': best_move
        }
    
    return (best_score, best_move) if ply == 0 else best_score

def iterative_deepening(board):
    best_move = None
    prev_score = 0
    for depth in range(1, 100):
        if time_is_up:
            break
        if depth < 5:
            score, move = negamax(board, depth, -1000000, 1000000, 0, True)
        else:
            delta = 50
            alpha = prev_score - delta
            beta = prev_score + delta
            while True:
                score, move = negamax(board, depth, alpha, beta, 0, True)
                if time_is_up:
                    break
                if score <= alpha:
                    alpha -= delta
                    delta *= 2
                elif score >= beta:
                    beta += delta
                    delta *= 2
                else:
                    break
        if time_is_up:
            break
        if move is not None:
            best_move = move
            prev_score = score
        if prev_score >= MATE_THRESHOLD or prev_score <= -MATE_THRESHOLD:
            break
    return best_move

def next_move(fen: str) -> str:
    global search_start_time, time_is_up, nodes_searched, killer_moves, history_table
    
    board = chess.Board(fen)
    
    book_move = get_opening_move(board)
    if book_move and chess.Move.from_uci(book_move) in board.legal_moves:
        return book_move

    search_start_time = time.time()
    time_is_up = False
    nodes_searched = 0
    killer_moves = [[None, None] for _ in range(128)]
    history_table = [[[0]*64 for _ in range(64)] for _ in range(2)]
    
    if len(transposition_table) > 1500000:
        transposition_table.clear()

    best_move = iterative_deepening(board)
    
    if best_move is None or best_move not in board.legal_moves:
        legal = list(board.legal_moves)
        best_move = random.choice(legal) if legal else None
        
    return best_move.uci() if best_move else None

def get_best_move(fen: str) -> str:
    return next_move(fen)