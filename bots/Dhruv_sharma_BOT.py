import chess
import time
import random

pw = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]

kn = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bi = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

ro = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
]

qu = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

km = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]

ke = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

val = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
       chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}

pst = {chess.PAWN: pw, chess.KNIGHT: kn, chess.BISHOP: bi,
       chess.ROOK: ro, chess.QUEEN: qu}

cap_ord = {chess.PAWN: 1, chess.KNIGHT: 2, chess.BISHOP: 3,
           chess.ROOK: 4, chess.QUEEN: 5, chess.KING: 6}

cache = {}
killers = [[None, None] for _ in range(64)]
hist = [[0] * 64 for _ in range(64)]


def flip(sq):
    return sq ^ 56


def endgame(b):
    q = len(b.pieces(chess.QUEEN, chess.WHITE)) + len(b.pieces(chess.QUEEN, chess.BLACK))
    if q == 0:
        return True
    w = len(b.pieces(chess.KNIGHT, chess.WHITE)) + len(b.pieces(chess.BISHOP, chess.WHITE)) + len(b.pieces(chess.ROOK, chess.WHITE))
    bk = len(b.pieces(chess.KNIGHT, chess.BLACK)) + len(b.pieces(chess.BISHOP, chess.BLACK)) + len(b.pieces(chess.ROOK, chess.BLACK))
    return q == 1 and w <= 1 and bk <= 1


def score(b):
    if b.is_checkmate():
        return -30000 if b.turn else 30000
    if b.is_stalemate() or b.is_insufficient_material() or b.can_claim_draw():
        return 0

    eg = endgame(b)
    s = 0

    for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        t = pst[pt]
        for sq in b.pieces(pt, chess.WHITE):
            s += val[pt] + t[flip(sq)]
        for sq in b.pieces(pt, chess.BLACK):
            s -= val[pt] + t[sq]

    kt = ke if eg else km
    for sq in b.pieces(chess.KING, chess.WHITE):
        s += kt[flip(sq)]
    for sq in b.pieces(chess.KING, chess.BLACK):
        s -= kt[sq]

    wb = len(b.pieces(chess.BISHOP, chess.WHITE))
    bb = len(b.pieces(chess.BISHOP, chess.BLACK))
    if wb >= 2:
        s += 30
    if bb >= 2:
        s -= 30

    for c in [chess.WHITE, chess.BLACK]:
        sgn = 1 if c == chess.WHITE else -1
        pawns = b.pieces(chess.PAWN, c)
        seen = set()
        for sq in pawns:
            f = chess.square_file(sq)
            if f in seen:
                s -= 10 * sgn
            seen.add(f)
        for sq in pawns:
            f = chess.square_file(sq)
            has_neighbor = False
            if f > 0 and any(chess.square_file(p) == f - 1 for p in pawns):
                has_neighbor = True
            if f < 7 and any(chess.square_file(p) == f + 1 for p in pawns):
                has_neighbor = True
            if not has_neighbor:
                s -= 15 * sgn

    for sq in b.pieces(chess.ROOK, chess.WHITE):
        f = chess.square_file(sq)
        pc = 0
        for r in range(8):
            p = b.piece_at(chess.square(f, r))
            if p and p.piece_type == chess.PAWN:
                pc += 1
        if pc == 0:
            s += 15
        elif pc == 1:
            s += 7

    for sq in b.pieces(chess.ROOK, chess.BLACK):
        f = chess.square_file(sq)
        pc = 0
        for r in range(8):
            p = b.piece_at(chess.square(f, r))
            if p and p.piece_type == chess.PAWN:
                pc += 1
        if pc == 0:
            s -= 15
        elif pc == 1:
            s -= 7

    if not eg:
        for c in [chess.WHITE, chess.BLACK]:
            sgn = 1 if c == chess.WHITE else -1
            ksq = b.king(c)
            kf = chess.square_file(ksq)
            kr = chess.square_rank(ksq)
            sh = 0
            dr = 1 if c == chess.WHITE else -1
            for df in [-1, 0, 1]:
                nf = kf + df
                if 0 <= nf <= 7:
                    nr = kr + dr
                    if 0 <= nr <= 7:
                        p = b.piece_at(chess.square(nf, nr))
                        if p and p.piece_type == chess.PAWN and p.color == c:
                            sh += 10
            s += sh * sgn

    if b.has_castling_rights(chess.WHITE):
        s += 15
    if b.has_castling_rights(chess.BLACK):
        s -= 15

    mob = b.legal_moves.count()
    b.push(chess.Move.null())
    opp_mob = b.legal_moves.count()
    b.pop()

    if b.turn == chess.WHITE:
        s += mob * 2
        s -= opp_mob * 2
    else:
        s -= mob * 2
        s += opp_mob * 2

    return s if b.turn == chess.WHITE else -s


def sort_moves(b, moves, tt_move, ply):
    res = []
    for m in moves:
        w = 0
        if m == tt_move:
            w = 100000
        elif b.is_capture(m):
            vict = b.piece_type_at(m.to_square)
            att = b.piece_type_at(m.from_square)
            if vict and att:
                w = 10000 + cap_ord.get(vict, 0) * 100 - cap_ord.get(att, 0)
            else:
                w = 10000
        elif m.promotion:
            w = 9000 + (500 if m.promotion == chess.QUEEN else 0)
        else:
            p = min(ply, 63)
            if killers[p][0] == m:
                w = 8000
            elif killers[p][1] == m:
                w = 7000
            else:
                w = hist[m.from_square][m.to_square]
        res.append((w, m))
    res.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in res]


def qs(b, a, bt, d):
    sp = score(b)
    if sp >= bt:
        return bt
    if sp > a:
        a = sp
    if d <= 0:
        return a

    caps = []
    for m in b.legal_moves:
        if b.is_capture(m) or m.promotion:
            vict = b.piece_type_at(m.to_square)
            att = b.piece_type_at(m.from_square)
            w = 0
            if vict and att:
                w = cap_ord.get(vict, 0) * 100 - cap_ord.get(att, 0)
            if m.promotion:
                w += 500
            caps.append((w, m))
    caps.sort(key=lambda x: x[0], reverse=True)

    for _, m in caps:
        if not m.promotion:
            vict = b.piece_type_at(m.to_square)
            att = b.piece_type_at(m.from_square)
            if vict and att:
                if val.get(vict, 0) + 200 < val.get(att, 0) and sp + val.get(vict, 0) + 200 < a:
                    continue

        b.push(m)
        v = -qs(b, -bt, -a, d - 1)
        b.pop()
        if v >= bt:
            return bt
        if v > a:
            a = v
    return a


def ab(b, dep, a, bt, ply, dl, cnt):
    cnt[0] += 1
    if cnt[0] % 4096 == 0 and time.time() > dl:
        raise TimeoutError

    fen = b.fen()
    entry = cache.get(fen)
    tmv = None
    if entry and entry[0] >= dep:
        td, tv, tf, tm = entry
        tmv = tm
        if tf == 0:
            return tv
        elif tf == 1 and tv <= a:
            return a
        elif tf == 2 and tv >= bt:
            return bt

    if b.is_game_over():
        if b.is_checkmate():
            return -30000 + ply
        return 0

    if dep <= 0:
        return qs(b, a, bt, 8)

    ic = b.is_check()

    if not ic and dep >= 3 and ply > 0 and not endgame(b):
        b.push(chess.Move.null())
        nv = -ab(b, dep - 3, -bt, -bt + 1, ply + 1, dl, cnt)
        b.pop()
        if nv >= bt:
            return bt

    moves = list(b.legal_moves)
    moves = sort_moves(b, moves, tmv, min(ply, 63))

    bv = -99999
    bm = moves[0] if moves else None
    fl = 1
    searched = 0

    for m in moves:
        ext = 1 if ic else 0

        b.push(m)

        if searched == 0:
            v = -ab(b, dep - 1 + ext, -bt, -a, ply + 1, dl, cnt)
        else:
            if searched >= 4 and dep >= 3 and not ic and not b.is_capture(m) and not m.promotion:
                v = -ab(b, dep - 2 + ext, -a - 1, -a, ply + 1, dl, cnt)
            else:
                v = a + 1
            if v > a:
                v = -ab(b, dep - 1 + ext, -bt, -a, ply + 1, dl, cnt)

        b.pop()
        searched += 1

        if v > bv:
            bv = v
            bm = m

        if v > a:
            a = v
            fl = 0
            if not b.is_capture(m):
                hist[m.from_square][m.to_square] += dep * dep

        if a >= bt:
            fl = 2
            if not b.is_capture(m):
                k = min(ply, 63)
                if killers[k][0] != m:
                    killers[k][1] = killers[k][0]
                    killers[k][0] = m
            break

    cache[fen] = (dep, bv, fl, bm)
    return bv


def next_move(fen):
    global cache, killers, hist
    b = chess.Board(fen)
    dl = time.time() + 3.5
    best = None
    cnt = [0]

    moves = list(b.legal_moves)
    if len(moves) == 1:
        return str(moves[0])

    for m in b.legal_moves:
        b.push(m)
        if b.is_checkmate():
            b.pop()
            return str(m)
        b.pop()

    killers = [[None, None] for _ in range(64)]
    hist = [[0] * 64 for _ in range(64)]

    for dep in range(1, 30):
        try:
            a = -99999
            bt = 99999
            cur = None
            bv = -99999

            tm = cache.get(b.fen(), (0, 0, 0, None))[3] if b.fen() in cache else None
            ordered = sort_moves(b, moves, tm, 0)

            for m in ordered:
                b.push(m)
                v = -ab(b, dep - 1, -bt, -a, 1, dl, cnt)
                b.pop()

                if v > bv:
                    bv = v
                    cur = m
                if v > a:
                    a = v

            best = cur

            if bv > 29000 or bv < -29000:
                break

        except TimeoutError:
            break

    if best is None:
        best = random.choice(moves)

    return str(best)
