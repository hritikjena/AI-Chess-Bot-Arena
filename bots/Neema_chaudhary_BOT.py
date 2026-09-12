import chess
import chess.polyglot
import time
import math

piece_val_mg = {chess.PAWN: 82, chess.KNIGHT: 337, chess.BISHOP: 365, chess.ROOK: 477, chess.QUEEN: 1025, chess.KING: 0}
piece_val_eg = {chess.PAWN: 94, chess.KNIGHT: 281, chess.BISHOP: 297, chess.ROOK: 512, chess.QUEEN: 936, chess.KING: 0}
phase_weight = {chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 1, chess.ROOK: 2, chess.QUEEN: 4, chess.KING: 0}
TOTAL_PHASE = 16*0 + 4*1 + 4*1 + 4*2 + 2*4

MG_PAWN = [0,0,0,0,0,0,0,0,98,134,61,95,68,126,34,-11,-6,7,26,31,65,56,25,-20,-14,13,6,21,23,12,17,-23,-27,-2,-5,12,17,6,10,-25,-26,-4,-4,-10,3,3,33,-12,-35,-1,-20,-23,-15,24,38,-22,0,0,0,0,0,0,0,0]
EG_PAWN = [0,0,0,0,0,0,0,0,178,173,158,134,147,132,165,187,94,100,85,67,56,53,82,84,32,24,13,5,-2,4,17,17,13,9,-3,-7,-7,-8,3,-1,4,7,-6,1,0,-5,-1,-8,13,8,8,10,13,0,2,-7,0,0,0,0,0,0,0,0]
MG_KNIGHT = [-167,-89,-34,-49,61,-97,-15,-107,-73,-41,72,36,23,62,7,-17,-47,60,37,65,84,129,73,44,-9,17,19,53,37,69,18,22,-13,4,16,13,28,19,21,-8,-23,-9,12,10,19,17,25,-16,-29,-53,-12,-3,-1,18,-14,-19,-105,-21,-58,-33,-17,-28,-19,-23]
EG_KNIGHT = [-58,-38,-13,-28,-31,-27,-63,-99,-25,-8,-25,-2,-9,-25,-24,-52,-24,-20,10,9,-1,-9,-19,-41,-17,3,22,22,22,11,8,-18,-18,-6,16,25,16,17,4,-18,-23,-3,-1,15,10,-3,-20,-22,-42,-20,-10,-5,-2,-20,-23,-44,-29,-51,-23,-15,-22,-18,-50,-64]
MG_BISHOP = [-29,4,-82,-37,-25,-42,7,-8,-26,16,-18,-13,30,59,18,-47,-16,37,43,40,35,50,37,-2,-4,5,19,50,37,37,7,-2,-6,13,13,26,34,12,10,4,0,15,15,15,14,27,18,10,4,15,16,0,7,21,33,1,-33,-3,-14,-21,-13,-12,-39,-21]
EG_BISHOP = [-14,-21,-11,-8,-7,-9,-17,-24,-8,-4,7,-12,-3,-13,-4,-14,2,-8,0,-1,-2,6,0,4,-3,9,12,9,14,10,3,2,-6,3,13,19,7,10,-3,-9,-12,-3,8,10,13,3,-7,-15,-14,-18,-7,-1,4,-9,-15,-27,-23,-9,-23,-5,-9,-16,-5,-17]
MG_ROOK = [32,42,32,51,63,9,31,43,27,32,58,62,80,67,26,44,-5,19,26,36,17,45,61,16,-24,-11,7,26,24,35,-8,-20,-36,-26,-12,-1,9,-7,6,-23,-45,-25,-16,-17,3,0,-5,-33,-44,-16,-20,-9,-1,11,-6,-71,-19,-13,1,17,16,7,-37,-26]
EG_ROOK = [13,10,18,15,12,-5,-7,6,11,13,13,11,-3,3,8,3,7,7,7,5,4,-3,-5,-3,4,3,13,1,2,1,-1,2,3,5,8,4,-5,-6,-8,-11,-4,0,-5,-1,-7,-12,-8,-16,-6,-6,0,2,-9,-9,-11,-3,-9,2,3,-1,-5,-13,4,-20]
MG_QUEEN = [-28,0,29,12,59,44,43,45,-24,-39,-5,1,-16,57,28,54,-13,-17,7,8,29,56,47,57,-27,-27,-16,-16,-1,17,-2,1,-9,-26,-9,-10,-2,-4,3,-3,-14,2,-11,-2,-5,2,14,5,-35,-8,11,2,8,15,-3,1,-1,-18,-9,10,-15,-25,-31,-50]
EG_QUEEN = [-9,22,22,27,27,19,10,20,-17,20,32,41,58,25,30,0,-20,6,9,49,47,35,19,9,3,22,24,45,57,40,57,36,-18,28,19,47,31,34,39,23,-16,-27,15,6,9,17,10,5,-22,-23,-30,-16,-16,-23,-36,-32,-33,-28,-22,-43,-5,-32,-20,-41]
MG_KING = [-65,23,16,-15,-56,-34,2,13,29,-1,-20,-7,-8,-4,-38,-29,-9,24,2,-16,-20,6,22,-22,-17,-20,-12,-27,-30,-25,-14,-36,-49,-1,-27,-39,-46,-44,-33,-51,-14,-14,-22,-46,-44,-30,-15,-27,1,7,-8,-64,-43,-16,9,8,-15,36,12,-54,8,-28,24,14]
EG_KING = [-74,-35,-18,-18,-11,15,4,-17,-12,17,14,17,17,38,23,11,10,17,23,15,20,45,44,13,-8,22,24,27,26,33,26,3,-18,-4,21,24,27,23,9,-11,-19,-3,11,21,23,16,7,-9,-27,-11,4,13,14,4,-5,-17,-53,-34,-21,-11,-28,-14,-24,-43]

MG_PASS = [0, 5, 10, 18, 35, 60, 100, 0]
EG_PASS = [0, 15, 30, 50, 90, 160, 280, 0]

MIRROR = [56 ^ sq for sq in range(64)]

PST = {
    chess.PAWN: (MG_PAWN, EG_PAWN),
    chess.KNIGHT: (MG_KNIGHT, EG_KNIGHT),
    chess.BISHOP: (MG_BISHOP, EG_BISHOP),
    chess.ROOK: (MG_ROOK, EG_ROOK),
    chess.QUEEN: (MG_QUEEN, EG_QUEEN),
    chess.KING: (MG_KING, EG_KING),
}

def pst_idx(sq, color):
    if color == chess.WHITE:
        return (7 - chess.square_rank(sq)) * 8 + chess.square_file(sq)
    return chess.square_rank(sq) * 8 + chess.square_file(sq)

def evaluate(board):
    mg_white = eg_white = mg_black = eg_black = 0
    phase = 0
    wm = bm = 0
    w_pc = [0]*8; b_pc = [0]*8
    w_pr = [[] for _ in range(8)]; b_pr = [[] for _ in range(8)]
    w_rooks = []; b_rooks = []
    w_bish = b_bish = 0
    w_pieces = b_pieces = 0

    for sq, p in board.piece_map().items():
        c = 0 if p.color else 1
        pt = p.piece_type
        i = pst_idx(sq, p.color)
        if c == 0:
            mg_white += piece_val_mg[pt] + PST[pt][0][i]
            eg_white += piece_val_eg[pt] + PST[pt][1][i]
        else:
            mg_black += piece_val_mg[pt] + PST[pt][0][i]
            eg_black += piece_val_eg[pt] + PST[pt][1][i]
        phase += phase_weight[pt]
        if pt != chess.KING:
            if c == 0: wm += piece_val_mg[pt]
            else: bm += piece_val_mg[pt]
            if pt != chess.PAWN:
                if c == 0: w_pieces += 1
                else: b_pieces += 1
        if pt == chess.PAWN:
            f = chess.square_file(sq)
            r = chess.square_rank(sq)
            if c == 0: w_pc[f] += 1; w_pr[f].append(r)
            else: b_pc[f] += 1; b_pr[f].append(r)
        elif pt == chess.ROOK:
            if c == 0: w_rooks.append(sq)
            else: b_rooks.append(sq)
        elif pt == chess.BISHOP:
            if c == 0: w_bish += 1
            else: b_bish += 1

    phase = min(phase, TOTAL_PHASE)
    mg_score = (mg_white - mg_black)
    eg_score = (eg_white - eg_black)
    score = (mg_score * phase + eg_score * (TOTAL_PHASE - phase)) // TOTAL_PHASE
    score += 14 * (1 if board.turn == chess.WHITE else -1)

    for f in range(8):
        if w_pc[f] > 1: score -= 12 * (w_pc[f]-1)
        if b_pc[f] > 1: score += 12 * (b_pc[f]-1)
        if w_pc[f] and (f == 0 or w_pc[f-1] == 0) and (f == 7 or w_pc[f+1] == 0):
            score -= 14
        if b_pc[f] and (f == 0 or b_pc[f-1] == 0) and (f == 7 or b_pc[f+1] == 0):
            score += 14

    for f in range(8):
        for r in w_pr[f]:
            passed = True
            for ff in range(max(0, f-1), min(8, f+2)):
                for br in b_pr[ff]:
                    if br > r: passed = False; break
                if not passed: break
            if passed:
                bonus = (MG_PASS[r] * phase + EG_PASS[r] * (TOTAL_PHASE-phase)) // TOTAL_PHASE
                wk = board.king(chess.WHITE)
                bk = board.king(chess.BLACK)
                if wk: bonus += max(0, 7 - chess.square_distance(wk, chess.square(f, r))) * 4
                if bk: bonus += min(chess.square_distance(bk, chess.square(f, r)) * 4, 24)
                score += bonus
        for r in b_pr[f]:
            passed = True
            for ff in range(max(0, f-1), min(8, f+2)):
                for wr in w_pr[ff]:
                    if wr < r: passed = False; break
                if not passed: break
            if passed:
                rr = 7 - r
                bonus = (MG_PASS[rr] * phase + EG_PASS[rr] * (TOTAL_PHASE-phase)) // TOTAL_PHASE
                bk = board.king(chess.BLACK)
                wk = board.king(chess.WHITE)
                if bk: bonus += max(0, 7 - chess.square_distance(bk, chess.square(f, r))) * 4
                if wk: bonus += min(chess.square_distance(wk, chess.square(f, r)) * 4, 24)
                score -= bonus

    if w_bish >= 2: score += 35
    if b_bish >= 2: score -= 35

    for sq in w_rooks:
        f = chess.square_file(sq)
        score += 22 if w_pc[f] == 0 and b_pc[f] == 0 else (12 if w_pc[f] == 0 else 0)
        if chess.square_rank(sq) == 6: score += 18
    for sq in b_rooks:
        f = chess.square_file(sq)
        score -= 22 if b_pc[f] == 0 and w_pc[f] == 0 else (12 if b_pc[f] == 0 else 0)
        if chess.square_rank(sq) == 1: score -= 18

    if phase > 6:
        wk = board.king(chess.WHITE)
        if wk:
            wkf, wkr = chess.square_file(wk), chess.square_rank(wk)
            shield = 0
            for df in range(max(0, wkf-1), min(8, wkf+2)):
                for wr in w_pr[df]:
                    if wr in (wkr+1, wkr+2): shield += 1
            score += shield * 10
            if wkf in (3, 4) and wkr <= 1: score -= 30
        bk = board.king(chess.BLACK)
        if bk:
            bkf, bkr = chess.square_file(bk), chess.square_rank(bk)
            shield = 0
            for df in range(max(0, bkf-1), min(8, bkf+2)):
                for br in b_pr[df]:
                    if br in (bkr-1, bkr-2): shield += 1
            score -= shield * 10
            if bkf in (3, 4) and bkr >= 6: score += 30

    if board.has_kingside_castling_rights(chess.WHITE): score += 15
    if board.has_queenside_castling_rights(chess.WHITE): score += 10
    if board.has_kingside_castling_rights(chess.BLACK): score -= 15
    if board.has_queenside_castling_rights(chess.BLACK): score -= 10

    adv = wm - bm
    wk = board.king(chess.WHITE)
    bk = board.king(chess.BLACK)

    if abs(adv) > 150 and wk and bk:
        kd = chess.square_distance(wk, bk)
        bkr, bkf = chess.square_rank(bk), chess.square_file(bk)
        wkr, wkf = chess.square_rank(wk), chess.square_file(wk)
        be = max(3-bkr, bkr-4, 3-bkf, bkf-4)
        we = max(3-wkr, wkr-4, 3-wkf, wkf-4)
        scale = min(abs(adv) // 100, 10)
        if adv > 0:
            score += (be * 70 + 14 - kd * 50) * scale // 3
        else:
            score -= (we * 70 + 14 - kd * 50) * scale // 3

    if phase <= 10 and wk and bk:
        bkr, bkf = chess.square_rank(bk), chess.square_file(bk)
        wkr, wkf = chess.square_rank(wk), chess.square_file(wk)
        wc = (3 - max(abs(wkr - 3), abs(wkf - 3)))
        bc = (3 - max(abs(bkr - 3), abs(bkf - 3)))
        score += wc * 12 - bc * 12

    if wk and bk:
        score += len(board.attackers(chess.WHITE, bk)) * 18
        score -= len(board.attackers(chess.BLACK, wk)) * 18

    if adv > 150:
        score -= board.halfmove_clock * 2
        score += (16 - w_pieces - b_pieces) * 15
    elif adv < -150:
        score += board.halfmove_clock * 2
        score -= (16 - w_pieces - b_pieces) * 15

    return score

EXACT, LOWER, UPPER = 0, 1, 2
MATE = 99000
MAX_PLY = 64

_tt = {}
_killers = [[None, None] for _ in range(MAX_PLY)]
_hist = {}
_counter = {}
_timeout = False
_start_time = 0
_time_limit = 3.0
_deadline = 0

def stm(board):
    s = evaluate(board)
    return s if board.turn == chess.WHITE else -s

def mvv_lva(board, move):
    v = board.piece_type_at(move.to_square)
    a = board.piece_type_at(move.from_square)
    vv = piece_val_mg[v] if v else 100
    av = piece_val_mg[a] if a else 100
    return vv * 10 - av

def mscore(board, move, ply, ttm, prev_move):
    if move == ttm: return 30000
    if move.promotion:
        s = 28000 if move.promotion == chess.QUEEN else 8000
        if board.is_capture(move):
            v = board.piece_type_at(move.to_square)
            if v: s += piece_val_mg[v]
        return s
    if board.is_capture(move):
        return 20000 + mvv_lva(board, move) if mvv_lva(board, move) >= 0 else mvv_lva(board, move)
    if board.gives_check(move): return 15000
    if ply < MAX_PLY:
        if move == _killers[ply][0]: return 12000
        if move == _killers[ply][1]: return 11000
    if prev_move and _counter.get((prev_move.from_square, prev_move.to_square)) == move:
        return 10500
    return _hist.get((move.from_square, move.to_square), 0)

def order_moves(board, ply, ttm=None, prev_move=None):
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: mscore(board, m, ply, ttm, prev_move), reverse=True)
    return moves

def qsearch(board, alpha, beta, ply):
    global _timeout
    if _timeout or (_deadline and time.time() > _deadline):
        _timeout = True
        return stm(board)

    in_check = board.is_check()
    if not in_check:
        sp = stm(board)
        if sp >= beta: return beta
        if sp > alpha: alpha = sp
    else:
        sp = -1000000

    moves = list(board.legal_moves)
    if in_check and not moves:
        return -MATE + ply

    moves.sort(key=lambda m: mscore(board, m, ply, None, None), reverse=True)

    for move in moves:
        is_cap = board.is_capture(move)
        is_promo = bool(move.promotion)
        if not in_check and not is_cap and not is_promo:
            continue
        if not in_check and is_cap and not is_promo:
            v = board.piece_type_at(move.to_square)
            if v and sp + piece_val_mg[v] + 200 < alpha:
                continue

        board.push(move)
        s = -qsearch(board, -beta, -alpha, ply + 1)
        board.pop()
        if _timeout: return sp if not in_check else 0
        if s >= beta: return beta
        if s > alpha: alpha = s

    return alpha

def pvs(board, depth, alpha, beta, ply=0, null_ok=True, prev_move=None):
    global _timeout
    if _timeout or (_deadline and time.time() > _deadline):
        _timeout = True
        return 0

    if ply > 0 and board.is_repetition(2):
        return -75

    in_check = board.is_check()
    if in_check: depth += 1

    is_pv = (beta - alpha) > 1
    tt_move = None
    tk = chess.polyglot.zobrist_hash(board)
    te = _tt.get(tk)
    if te:
        td, ts, tf, tm = te
        tt_move = tm
        if td >= depth and not is_pv:
            if tf == EXACT: return ts
            if tf == LOWER: alpha = max(alpha, ts)
            if tf == UPPER: beta = min(beta, ts)
            if alpha >= beta: return ts

    if depth <= 0:
        return qsearch(board, alpha, beta, ply)

    se = stm(board)
    pieces = len(board.piece_map())

    if not is_pv and not in_check and depth <= 3:
        margin = 200 + 150 * depth
        if se + margin <= alpha:
            rs = qsearch(board, alpha, beta, ply)
            if rs <= alpha: return rs

    if null_ok and depth >= 3 and not in_check and pieces > 10 and not is_pv:
        R = 3 if depth >= 6 else 2
        board.push(chess.Move.null())
        ns = -pvs(board, depth - 1 - R, -beta, -beta + 1, ply + 1, False, None)
        board.pop()
        if _timeout: return 0
        if ns >= beta:
            if depth >= 8:
                vs = pvs(board, depth - 1 - R, beta - 1, beta, ply, False, prev_move)
                if vs >= beta: return beta
            else:
                return beta

    moves = order_moves(board, ply, tt_move, prev_move)
    if not moves:
        return (-MATE + ply) if in_check else 0

    best = -1000000; bmv = None; oa = alpha; searched = 0; quiets = 0

    for move in moves:
        if _timeout: break
        is_cap = board.is_capture(move)
        gives_chk = board.gives_check(move)
        is_promo = bool(move.promotion)
        tactical = is_cap or gives_chk or is_promo

        if not is_pv and depth <= 3 and not in_check and not tactical:
            if quiets >= 5 + depth * 3:
                continue

        board.push(move)

        if searched == 0:
            s = -pvs(board, depth - 1, -beta, -alpha, ply + 1, True, move)
        else:
            reduction = 0
            if searched >= 3 and depth >= 3 and not in_check and not tactical:
                reduction = max(0, int(0.75 + math.log(depth) * math.log(searched) / 2.25))
                if is_pv: reduction = max(0, reduction - 1)
                h = _hist.get((move.from_square, move.to_square), 0)
                if h < 0: reduction += 1
                reduction = min(reduction, depth - 2)

            s = -pvs(board, depth - 1 - reduction, -alpha - 1, -alpha, ply + 1, True, move)

            if reduction > 0 and s > alpha and not _timeout:
                s = -pvs(board, depth - 1, -alpha - 1, -alpha, ply + 1, True, move)

            if s > alpha and s < beta and not _timeout:
                s = -pvs(board, depth - 1, -beta, -alpha, ply + 1, True, move)

        board.pop()
        searched += 1
        if not tactical: quiets += 1

        if s > best:
            best = s; bmv = move
        alpha = max(alpha, s)
        if alpha >= beta:
            if not is_cap and ply < MAX_PLY:
                if _killers[ply][0] != move:
                    _killers[ply][1] = _killers[ply][0]
                    _killers[ply][0] = move
            if prev_move and not is_cap:
                _counter[(prev_move.from_square, prev_move.to_square)] = move
            _hist[(move.from_square, move.to_square)] = _hist.get((move.from_square, move.to_square), 0) + depth * depth
            break

    if best > -1000000:
        flag = EXACT if oa < best < beta else (LOWER if best >= beta else UPPER)
        old = _tt.get(tk)
        if old is None or depth >= old[0]:
            if len(_tt) > 400000:
                _tt.clear()
            _tt[tk] = (depth, best, flag, bmv)

    return best

def search(board, tl=3.0):
    global _killers, _hist, _counter, _timeout, _deadline
    _killers = [[None, None] for _ in range(MAX_PLY)]
    _hist = {}
    _counter = {}
    _timeout = False
    _start = time.time()
    _deadline = _start + tl

    moves = order_moves(board, 0)
    if not moves: return None
    if len(moves) == 1: return moves[0]

    best = moves[0]
    prev_score = 0
    pieces = len(board.piece_map())
    max_d = 20 if pieces <= 6 else (16 if pieces <= 10 else (14 if pieces <= 16 else 12))

    for depth in range(1, max_d + 1):
        elapsed = time.time() - _start
        if elapsed > tl * 0.65: break

        _timeout = False

        if depth >= 4:
            window = 30
            a_lo = prev_score - window
            a_hi = prev_score + window
        else:
            a_lo = -1000000; a_hi = 1000000

        for attempt in range(4):
            cb = None; cs = -1000000

            for move in moves:
                if time.time() >= _deadline:
                    _timeout = True
                    break

                board.push(move)
                if board.is_repetition(2):
                    s = -75
                else:
                    s = -pvs(board, depth - 1, -a_hi, -a_lo, 1, True, move)
                board.pop()

                if _timeout: break
                if s > cs: cs = s; cb = move

            if _timeout: break

            if cs <= a_lo:
                a_lo = max(a_lo - window * 4, -1000000)
                window *= 4
                if cb: best = cb
                continue
            elif cs >= a_hi:
                a_hi = min(a_hi + window * 4, 1000000)
                window *= 4
                if cb: best = cb
                continue
            else:
                break

        if cb and not _timeout:
            best = cb
            prev_score = cs
            if cb in moves:
                moves.remove(cb)
                moves.insert(0, cb)

        if prev_score >= MATE - 100: break

    return best

def next_move(fen):
    try:
        board = chess.Board(fen)

        for move in board.legal_moves:
            board.push(move)
            if board.is_checkmate():
                board.pop()
                return str(move)
            board.pop()

        result = search(board, tl=_time_limit)
        if result is None:
            moves = list(board.legal_moves)
            return str(moves[0]) if moves else ""
        return str(result)
    except Exception:
        board = chess.Board(fen)
        moves = list(board.legal_moves)
        return str(moves[0]) if moves else ""

if __name__ == '__main__':
    import chess
    tests = ['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1']
    for fen in tests:
        b = chess.Board(fen)
        t = time.time()
        m = next_move(fen)
        print(f'{time.time()-t:.2f}s | {m}')