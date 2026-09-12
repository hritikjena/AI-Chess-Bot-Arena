import chess
import chess.polyglot
import time

PIECE_VALUES = {1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 0, None: 0}

P_PST = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10,-20,-20, 10, 10, 5,
    5, -5,-10, 0, 0,-10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]

N_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

B_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

R_PST = [
    0,  0,  0,  5,  5,  0,  0,  0,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   25, 30, 30, 30, 30, 30, 30, 25,
    0,  0,  0,  0,  0,  0,  0,  0
]

Q_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
      0,  0,  5,  5,  5,  5,  0, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

K_PST = [
    20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30
]

K_PST_E = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -30,  0,  0,  0,  0,  0,  0,-30,
    -30,  0, 20, 30, 30, 20,  0,-30,
    -30,  0, 30, 40, 40, 30,  0,-30,
    -30,  0, 30, 40, 40, 30,  0,-30,
    -30,  0, 20, 30, 30, 20,  0,-30,
    -30,  0,  0,  0,  0,  0,  0,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

PASSED_BONUS = [0, 20, 40, 70, 110, 160, 250, 0]

def evaluate(board):
    if board.is_checkmate(): return -30000
    if board.is_game_over(): return 0
    score = 0
    
    total_material = sum(
        (len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK))) * val
        for pt, pst, val in [(1, P_PST, 100), (2, N_PST, 320), (3, B_PST, 330), (4, R_PST, 500), (5, Q_PST, 900)]
    )
    is_endgame = total_material < 2400
    
    for pt, pst, val in [(1, P_PST, 100), (2, N_PST, 320), (3, B_PST, 330), (4, R_PST, 500), (5, Q_PST, 900)]:
        w = board.pieces(pt, chess.WHITE)
        b = board.pieces(pt, chess.BLACK)
        score += (len(w) - len(b)) * val
        for sq in w: score += pst[sq]
        for sq in b: score -= pst[chess.square_mirror(sq)]
        
    k_pst = K_PST_E if is_endgame else K_PST
    for sq in board.pieces(6, chess.WHITE): score += k_pst[sq]
    for sq in board.pieces(6, chess.BLACK): score -= k_pst[chess.square_mirror(sq)]

    if is_endgame:
        for sq in board.pieces(6, chess.WHITE):
            score += (3 - min(chess.square_file(sq), 7-chess.square_file(sq))) * 5
            score += (3 - min(chess.square_rank(sq), 7-chess.square_rank(sq))) * 5
        for sq in board.pieces(6, chess.BLACK):
            score -= (3 - min(chess.square_file(sq), 7-chess.square_file(sq))) * 5
            score -= (3 - min(chess.square_rank(sq), 7-chess.square_rank(sq))) * 5

        wk = board.king(chess.WHITE)
        bk = board.king(chess.BLACK)
        if wk is not None and bk is not None:
            if score > 100:
                cmd = abs(chess.square_file(bk)-3) + abs(chess.square_rank(bk)-3)
                dist = chess.square_distance(wk, bk)
                score += 4 * cmd + 2 * (14 - dist)
            elif score < -100:
                cmd = abs(chess.square_file(wk)-3) + abs(chess.square_rank(wk)-3)
                dist = chess.square_distance(wk, bk)
                score -= 4 * cmd + 2 * (14 - dist)

    if len(board.pieces(3, chess.WHITE)) >= 2: score += 50
    if len(board.pieces(3, chess.BLACK)) >= 2: score -= 50

    for c in [chess.WHITE, chess.BLACK]:
        sign = 1 if c == chess.WHITE else -1
        pawns = list(board.pieces(1, c))
        enemy_pawns = list(board.pieces(1, not c))
        p_files = [chess.square_file(sq) for sq in pawns]
        e_files = [chess.square_file(sq) for sq in enemy_pawns]
        
        for sq in pawns:
            f, r = chess.square_file(sq), chess.square_rank(sq)
            if p_files.count(f) > 1: score -= 20 * sign
            if f-1 not in p_files and f+1 not in p_files: score -= 15 * sign
            
            is_passed = True
            for er in (range(r+1, 8) if c == chess.WHITE else range(r-1, -1, -1)):
                if chess.square(f, er) in enemy_pawns: is_passed = False; break
                if f > 0 and chess.square(f-1, er) in enemy_pawns: is_passed = False; break
                if f < 7 and chess.square(f+1, er) in enemy_pawns: is_passed = False; break
            if is_passed: 
                rank_idx = r if c == chess.WHITE else 7 - r
                score += PASSED_BONUS[rank_idx] * sign
            
        for sq in board.pieces(4, c):
            f = chess.square_file(sq)
            if f not in p_files:
                if f not in e_files: score += 20 * sign
                else: score += 10 * sign

    if score > 0: score -= board.halfmove_clock * 5
    elif score < 0: score += board.halfmove_clock * 5

    return score if board.turn == chess.WHITE else -score

TT = {}
KILLERS = [[None, None] for _ in range(128)]
HISTORY = [[0 for _ in range(64)] for _ in range(64)]

def quiescence(board, alpha, beta, start, limit, qdepth=0):
    if time.time() - start > limit: raise TimeoutError
    
    is_check = board.is_check()
    if not is_check:
        stand_pat = evaluate(board)
        if stand_pat >= beta: return beta
        alpha = max(alpha, stand_pat)
        if qdepth > 4: return alpha
        caps = sorted([m for m in board.legal_moves if board.is_capture(m)], 
                      key=lambda m: PIECE_VALUES.get(board.piece_type_at(m.to_square), 0), reverse=True)
        if not caps: return alpha
    else:
        stand_pat = -30000
        caps = list(board.legal_moves)
        caps = sorted(caps, key=lambda m: PIECE_VALUES.get(board.piece_type_at(m.to_square), 0), reverse=True)
    
    for m in (caps[:8] if not is_check else caps):
        if not is_check:
            val = PIECE_VALUES.get(board.piece_type_at(m.to_square), 0)
            if m.promotion: val += 800
            if stand_pat + val + 200 < alpha and not board.gives_check(m):
                continue
            
        board.push(m)
        v = -quiescence(board, -beta, -alpha, start, limit, qdepth + 1)
        if v > 20000: v -= 1
        elif v < -20000: v += 1
        board.pop()
        
        if v >= beta: return beta
        alpha = max(alpha, v)
        
    if not caps and is_check: return -30000
    
    return alpha

def alpha_beta(board, depth, alpha, beta, start, limit, can_null=True):
    if time.time() - start > limit: raise TimeoutError
    
    original_alpha = alpha
    key = chess.polyglot.zobrist_hash(board)
    tt_entry = TT.get(key)
    if tt_entry and tt_entry['d'] >= depth:
        if tt_entry['f'] == 'E': return tt_entry['v']
        elif tt_entry['f'] == 'L': alpha = max(alpha, tt_entry['v'])
        elif tt_entry['f'] == 'U': beta = min(beta, tt_entry['v'])
        if alpha >= beta: return tt_entry['v']

    if depth <= 0 or board.is_game_over(): 
        return quiescence(board, alpha, beta, start, limit)
        
    if board.is_repetition(2):
        return 0
        
    is_check = board.is_check()
    
    non_pawn = sum(len(board.pieces(pt, c)) * v for pt, v in [(2,320),(3,330),(4,500),(5,900)] for c in [chess.WHITE, chess.BLACK])
    if can_null and depth >= 3 and not is_check and non_pawn > 1200:
        board.push(chess.Move.null())
        try: v = -alpha_beta(board, depth - 3, -beta, -beta + 1, start, limit, False)
        finally: board.pop()
        if v >= beta: return v

    best_v = -30000
    best_m = None
    tt_m = tt_entry['m'] if tt_entry else None
    
    k1 = KILLERS[depth][0] if depth < 128 else None
    k2 = KILLERS[depth][1] if depth < 128 else None
    
    def move_score(m):
        if m == tt_m: return 1000000
        if board.is_capture(m): 
            return 10000 + PIECE_VALUES.get(board.piece_type_at(m.to_square), 0) - PIECE_VALUES.get(board.piece_type_at(m.from_square), 0) / 10
        if m == k1: return 9000
        if m == k2: return 8000
        return HISTORY[m.from_square][m.to_square]
        
    moves = sorted(list(board.legal_moves), key=move_score, reverse=True)
    
    for i, m in enumerate(moves):
        is_capture = board.is_capture(m)
        board.push(m)
        try:
            is_pv_move = (i == 0)
            causes_check = board.is_check()
            new_depth = depth - 1
            
            if not is_pv_move and new_depth >= 3 and i >= 3 and not is_capture and not is_check and not causes_check:
                v = -alpha_beta(board, new_depth - 1, -alpha - 1, -alpha, start, limit, True)
                if v > 20000: v -= 1
                elif v < -20000: v += 1
                
                if v > alpha: 
                    v = -alpha_beta(board, new_depth, -beta, -alpha, start, limit, True)
                    if v > 20000: v -= 1
                    elif v < -20000: v += 1
            else:
                if is_pv_move:
                    v = -alpha_beta(board, new_depth, -beta, -alpha, start, limit, True)
                    if v > 20000: v -= 1
                    elif v < -20000: v += 1
                else:
                    v = -alpha_beta(board, new_depth, -alpha - 1, -alpha, start, limit, True)
                    if v > 20000: v -= 1
                    elif v < -20000: v += 1
                    
                    if alpha < v < beta:
                        v = -alpha_beta(board, new_depth, -beta, -alpha, start, limit, True)
                        if v > 20000: v -= 1
                        elif v < -20000: v += 1
        finally: board.pop()
        
        if v > best_v: 
            best_v, best_m = v, m
            
        alpha = max(alpha, v)
        if alpha >= beta:
            if not is_capture and depth < 128:
                if KILLERS[depth][0] != m:
                    KILLERS[depth][1] = KILLERS[depth][0]
                    KILLERS[depth][0] = m
                HISTORY[m.from_square][m.to_square] += depth * depth
            break
            
    flag = 'E'
    if best_v <= original_alpha: 
        flag = 'U'
        store_score = original_alpha
    elif best_v >= beta: 
        flag = 'L'
        store_score = best_v
    else:
        store_score = best_v
        
    TT[key] = {'d': depth, 'm': best_m, 'v': store_score, 'f': flag}
    return best_v

OPENING_BOOK = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": "e2e4",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6": "g1f3",
    "rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -": "d2d4",
    "r1bqkbnr/pp2pppp/2np4/8/3NP3/8/PPP2PPP/RNBQKB1R w KQkq -": "b1c3",
    "r1bqkb1r/pp2pppp/2np1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq -": "f1c4",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3": "c7c5",
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3": "g8f6",
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3": "e7e5",
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -": "d7d5",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": "d7d6",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq -": "b8c6",
    "rnbqkbnr/pp2pppp/3p4/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq d3": "c5d4",
    "r1bqkbnr/pp2pppp/2np4/8/3NP3/8/PPP2PPP/RNBQKB1R b KQkq -": "g8f6",
    "r1bqkb1r/pp2pppp/2np1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R b KQkq -": "e7e6",
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq -": "c2c4",
    "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3": "e7e6",
    "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -": "g1f3",
    "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/5N2/PP2PPPP/RNBQKB1R w KQkq -": "c1d2",
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3": "e7e6",
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq -": "g8f6",
    "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR b KQkq -": "c7c5",
    "rnbqkb1r/pp1p1ppp/4pn2/2p5/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq c6": "d4d5"
}

def next_move(fen):
    global TT, KILLERS, HISTORY
    board = chess.Board(fen)
    
    fen_key = " ".join(fen.split()[:4])
    if fen_key in OPENING_BOOK and chess.Move.from_uci(OPENING_BOOK[fen_key]) in board.legal_moves:
        return OPENING_BOOK[fen_key]
        
    start = time.time()
    best_move = None
    last_score = None
    
    if len(TT) > 200000:
        TT.clear()
        
    for i in range(64):
        for j in range(64):
            HISTORY[i][j] //= 2
            
    legal_moves = sorted(list(board.legal_moves), key=lambda m: (
        m.to_square in [chess.D4, chess.E4, chess.D5, chess.E5],
        board.is_capture(m)
    ), reverse=True)
    if not legal_moves: return None
    
    try:
        for depth in range(1, 40):
            if depth > 2 and last_score is not None:
                alpha = last_score - 50
                beta = last_score + 50
            else:
                alpha = -30000
                beta = 30000
                
            while True:
                score = alpha_beta(board, depth, alpha, beta, start, 3.0, True)
                if score <= alpha:
                    alpha = -30000
                elif score >= beta:
                    beta = 30000
                else:
                    last_score = score
                    break
                if alpha == -30000 and beta == 30000:
                    last_score = score
                    break
                    
            res = TT.get(chess.polyglot.zobrist_hash(board))
            if res and res.get('m'): best_move = res['m']
            
            if time.time() - start > 3.0: break 
    except TimeoutError:
        pass
        
    if not best_move or best_move not in legal_moves: 
        best_move = legal_moves[0]
        
    return str(best_move)