import chess
import chess.polyglot
import time
import random
piece_val = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
pawn_table = [0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10, 5, 5, 10, 25, 25, 10, 5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, -5, -10, 0, 0, -10, -5, 5, 5, 10, 10, -20, -20, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0]
knight_table = [-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 0, 0, 0, -20, -40, -30, 0, 10, 15, 15, 10, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 10, 15, 15, 10, 5, -30, -40, -20, 0, 5, 5, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50]
bishop_table = [-20, -10, -10, -10, -10, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 5, 0, 0, 0, 0, 5, -10, -20, -10, -10, -10, -10, -10, -10, -20]
rook_table = [0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, 10, 10, 10, 10, 5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 5, 5, 0, 0, 0]
queen_table = [-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 5, 5, 5, 0, -10, -5, 0, 5, 5, 5, 5, 0, -5, 0, 0, 5, 5, 5, 5, 0, -5, -10, 5, 5, 5, 5, 5, 0, -10, -10, 0, 5, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20]
king_mid_table = [-30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -20, -30, -30, -40, -40, -30, -30, -20, -10, -20, -20, -20, -20, -20, -20, -10, 20, 20, 0, 0, 0, 0, 20, 20, 20, 30, 10, 0, 0, 10, 30, 20]
king_end_table = [-50, -40, -30, -20, -20, -30, -40, -50, -30, -20, -10, 0, 0, -10, -20, -30, -30, -10, 20, 30, 30, 20, -10, -30, -30, -10, 30, 40, 40, 30, -10, -30, -30, -10, 30, 40, 40, 30, -10, -30, -30, -10, 20, 30, 30, 20, -10, -30, -30, -30, 0, 0, 0, 0, -30, -30, -50, -30, -30, -30, -30, -30, -30, -50]
pawn_end_table = [0, 0, 0, 0, 0, 0, 0, 0, 80, 80, 80, 80, 80, 80, 80, 80, 50, 50, 50, 50, 50, 50, 50, 50, 30, 30, 30, 30, 30, 30, 30, 30, 20, 20, 20, 20, 20, 20, 20, 20, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0]

def _flip(sq):
    return (7 - (sq >> 3)) * 8 + (sq & 7)
pst_lookup = {}
for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
    pst_lookup[pt] = {}
    mid = {chess.PAWN: pawn_table, chess.KNIGHT: knight_table, chess.BISHOP: bishop_table, chess.ROOK: rook_table, chess.QUEEN: queen_table, chess.KING: king_mid_table}[pt]
    end = {chess.PAWN: pawn_end_table, chess.KING: king_end_table}.get(pt, mid)
    for color in [chess.WHITE, chess.BLACK]:
        pst_lookup[pt][color] = {}
        for sq in range(64):
            idx = _flip(sq) if color == chess.WHITE else sq
            pst_lookup[pt][color][sq] = (mid[idx], end[idx])

def evaluate(board):
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if board.can_claim_draw():
        return 0
    phase = 0
    for color in [chess.WHITE, chess.BLACK]:
        phase += len(board.pieces(chess.KNIGHT, color))
        phase += len(board.pieces(chess.BISHOP, color))
        phase += len(board.pieces(chess.ROOK, color)) * 2
        phase += len(board.pieces(chess.QUEEN, color)) * 4
    phase = min(phase, 24)
    phase = (phase * 256 + 12) // 24
    score = 0
    mg_pst = 0
    eg_pst = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        pt = piece.piece_type
        mg_b, eg_b = pst_lookup[pt][piece.color][sq]
        if piece.color == chess.WHITE:
            score += piece_val.get(pt, 0)
            mg_pst += mg_b
            eg_pst += eg_b
        else:
            score -= piece_val.get(pt, 0)
            mg_pst -= mg_b
            eg_pst -= eg_b
    score += (mg_pst * phase + eg_pst * (256 - phase)) // 256
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += 30
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= 30
    wp = board.pieces(chess.PAWN, chess.WHITE)
    bp = board.pieces(chess.PAWN, chess.BLACK)
    wf = [0] * 8
    bf = [0] * 8
    for sq in wp:
        wf[chess.square_file(sq)] += 1
    for sq in bp:
        bf[chess.square_file(sq)] += 1
    for f in range(8):
        if wf[f] > 1:
            score -= 10 * (wf[f] - 1)
        if bf[f] > 1:
            score += 10 * (bf[f] - 1)
        has_n_w = f > 0 and wf[f - 1] > 0 or (f < 7 and wf[f + 1] > 0)
        has_n_b = f > 0 and bf[f - 1] > 0 or (f < 7 and bf[f + 1] > 0)
        if wf[f] > 0 and (not has_n_w):
            score -= 12
        if bf[f] > 0 and (not has_n_b):
            score += 12
    for sq in wp:
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        passed = True
        for cr in range(r + 1, 8):
            for df in [f - 1, f, f + 1]:
                if 0 <= df <= 7 and chess.square(df, cr) in bp:
                    passed = False
                    break
            if not passed:
                break
        if passed:
            score += 15 + r * 8
    for sq in bp:
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        passed = True
        for cr in range(0, r):
            for df in [f - 1, f, f + 1]:
                if 0 <= df <= 7 and chess.square(df, cr) in wp:
                    passed = False
                    break
            if not passed:
                break
        if passed:
            score -= 15 + (7 - r) * 8
    wp_f = set((chess.square_file(sq) for sq in wp))
    bp_f = set((chess.square_file(sq) for sq in bp))
    for sq in board.pieces(chess.ROOK, chess.WHITE):
        f = chess.square_file(sq)
        if f not in wp_f and f not in bp_f:
            score += 15
        elif f not in wp_f:
            score += 7
    for sq in board.pieces(chess.ROOK, chess.BLACK):
        f = chess.square_file(sq)
        if f not in wp_f and f not in bp_f:
            score -= 15
        elif f not in bp_f:
            score -= 7
    return score
victim_score = {chess.PAWN: 10, chess.KNIGHT: 30, chess.BISHOP: 30, chess.ROOK: 50, chess.QUEEN: 90, chess.KING: 0}
attacker_score = {chess.PAWN: 1, chess.KNIGHT: 2, chess.BISHOP: 3, chess.ROOK: 4, chess.QUEEN: 5, chess.KING: 6}
mvv_lva = {}
for v in victim_score:
    for a in attacker_score:
        mvv_lva[v, a] = victim_score[v] * 10 - attacker_score[a]
killers = [[None, None] for _ in range(64)]
history = [[0] * 64 for _ in range(64)]

def order_moves(board, moves, ply, tt_move=None):
    scored = []
    for m in moves:
        s = 0
        if m == tt_move:
            s = 10000000
        elif board.is_capture(m):
            victim = board.piece_type_at(m.to_square)
            if victim is None:
                victim = chess.PAWN
            attacker = board.piece_type_at(m.from_square)
            s = 1000000 + mvv_lva.get((victim, attacker), 0)
        elif m.promotion:
            s = 900000 + piece_val.get(m.promotion, 0)
        elif ply < 64 and m == killers[ply][0]:
            s = 800000
        elif ply < 64 and m == killers[ply][1]:
            s = 700000
        else:
            s = history[m.from_square][m.to_square]
        scored.append((s, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]
EXACT = 0
ALPHA_FLAG = 1
BETA_FLAG = 2

class TTEntry:
    __slots__ = ['key', 'depth', 'score', 'flag', 'move']

    def __init__(self, key, depth, score, flag, move):
        self.key = key
        self.depth = depth
        self.score = score
        self.flag = flag
        self.move = move
tt_size = 1 << 18
tt = [None] * tt_size

def tt_store(key, depth, score, flag, move):
    idx = key % tt_size
    entry = tt[idx]
    if entry is None or depth >= entry.depth:
        tt[idx] = TTEntry(key, depth, score, flag, move)

def tt_lookup(key):
    idx = key % tt_size
    entry = tt[idx]
    if entry and entry.key == key:
        return entry
    return None
CHECKMATE = 99999
start_time = 0
time_limit = 3.0
time_up = False
nodes = 0

def check_time():
    global time_up
    if time.time() - start_time >= time_limit:
        time_up = True

def has_big_pieces(board):
    c = board.turn
    return bool(board.pieces(chess.KNIGHT, c) or board.pieces(chess.BISHOP, c) or board.pieces(chess.ROOK, c) or board.pieces(chess.QUEEN, c))

def quiescence(board, alpha, beta, ply):
    global nodes, time_up
    if time_up:
        return 0
    if nodes & 1023 == 0:
        check_time()
        if time_up:
            return 0
    nodes += 1
    stand_pat = evaluate(board)
    if board.turn == chess.BLACK:
        stand_pat = -stand_pat
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    captures = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
    captures = order_moves(board, captures, ply)
    for move in captures:
        if board.is_capture(move) and (not move.promotion):
            victim = board.piece_type_at(move.to_square)
            if victim and stand_pat + piece_val.get(victim, 0) + 200 < alpha:
                continue
        board.push(move)
        score = -quiescence(board, -beta, -alpha, ply + 1)
        board.pop()
        if time_up:
            return 0
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha

def alphabeta(board, depth, alpha, beta, ply, allow_null=True):
    global nodes, time_up
    if time_up:
        return 0
    if nodes & 1023 == 0:
        check_time()
        if time_up:
            return 0
    nodes += 1
    if board.is_repetition(2) or board.halfmove_clock >= 100:
        return 0
    is_pv = beta - alpha > 1
    original_alpha = alpha
    tt_key = chess.polyglot.zobrist_hash(board)
    tt_move = None
    entry = tt_lookup(tt_key)
    if entry and entry.depth >= depth:
        tt_move = entry.move
        if not is_pv:
            if entry.flag == EXACT:
                return entry.score
            elif entry.flag == ALPHA_FLAG and entry.score <= alpha:
                return alpha
            elif entry.flag == BETA_FLAG and entry.score >= beta:
                return beta
    elif entry:
        tt_move = entry.move
    if depth <= 0:
        return quiescence(board, alpha, beta, ply)
    in_check = board.is_check()
    if in_check:
        depth += 1
    if allow_null and (not in_check) and (not is_pv) and (depth >= 3) and has_big_pieces(board):
        R = 2 if depth < 6 else 3
        board.push(chess.Move.null())
        score = -alphabeta(board, depth - 1 - R, -beta, -beta + 1, ply + 1, False)
        board.pop()
        if time_up:
            return 0
        if score >= beta:
            return beta
    moves = list(board.legal_moves)
    if not moves:
        if in_check:
            return -CHECKMATE + ply
        return 0
    moves = order_moves(board, moves, ply, tt_move)
    best_score = -CHECKMATE - 1
    best_move = moves[0]
    for i, move in enumerate(moves):
        board.push(move)
        if i >= 4 and depth >= 3 and (not in_check) and (not board.is_check()) and (not board.is_capture(move)) and (not move.promotion):
            score = -alphabeta(board, depth - 2, -alpha - 1, -alpha, ply + 1)
            if score > alpha:
                score = -alphabeta(board, depth - 1, -beta, -alpha, ply + 1)
        elif not is_pv or i == 0:
            score = -alphabeta(board, depth - 1, -beta, -alpha, ply + 1)
        else:
            score = -alphabeta(board, depth - 1, -alpha - 1, -alpha, ply + 1)
            if alpha < score < beta:
                score = -alphabeta(board, depth - 1, -beta, -alpha, ply + 1)
        board.pop()
        if time_up:
            return 0
        if score > best_score:
            best_score = score
            best_move = move
        if score > alpha:
            alpha = score
            if not board.is_capture(move):
                history[move.from_square][move.to_square] += depth * depth
        if alpha >= beta:
            if not board.is_capture(move) and ply < 64:
                if move != killers[ply][0]:
                    killers[ply][1] = killers[ply][0]
                    killers[ply][0] = move
            break
    if best_score <= original_alpha:
        flag = ALPHA_FLAG
    elif best_score >= beta:
        flag = BETA_FLAG
    else:
        flag = EXACT
    tt_store(tt_key, depth, best_score, flag, best_move)
    return best_score

def find_best_move(board):
    global start_time, time_up, nodes
    start_time = time.time()
    time_up = False
    nodes = 0
    moves = list(board.legal_moves)
    if len(moves) == 1:
        return moves[0]
    best = None
    for depth in range(1, 64):
        if time_up:
            break
        score = alphabeta(board, depth, -CHECKMATE - 1, CHECKMATE + 1, 0)
        if time_up and depth == 1:
            if best is None:
                best = moves[0]
            break
        if not time_up:
            key = chess.polyglot.zobrist_hash(board)
            entry = tt_lookup(key)
            if entry and entry.move:
                best = entry.move
        elapsed = time.time() - start_time
        if elapsed > time_limit * 0.55:
            break
        if abs(score) >= CHECKMATE - 64:
            break
    if best is None:
        best = random.choice(moves)
    return best

def next_move(fen):
    board = chess.Board(fen)
    move = find_best_move(board)
    return str(move)
if __name__ == '__main__':
    print('testing bot...')
    test_positions = ['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 'rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2', '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1']
    for fen in test_positions:
        b = chess.Board(fen)
        print(f'\n{b}\n')
        t = time.time()
        m = next_move(fen)
        print(f'move: {m} ({time.time() - t:.2f}s)')
    print('\ndone!')