#!/usr/bin/env python3

import sys
import time
import random
import chess

INF          = 10_000_000
MATE         = 32_000
MATE_BOUND   = MATE - 1024
TIME_LIMIT   = 3.7
SOFT_LIMIT   = 3.0
MAX_PLY      = 128

PIECE_IDX = {'P':0,'N':1,'B':2,'R':3,'Q':4,'K':5,
             'p':0,'n':1,'b':2,'r':3,'q':4,'k':5}

MG_VAL = [82, 337, 365, 477, 1025, 0]
EG_VAL = [94, 281, 297, 512,  936, 0]
PHASE_INC   = [0, 1, 1, 2, 4, 0]
TOTAL_PHASE = 24

# PeSTO PSTs (white POV, idx 0=a1 … 63=h8)
MG_P = [
      0,   0,   0,   0,   0,   0,   0,   0,
    -35,  -1, -20, -23, -15,  24,  38, -22,
    -26,  -4,  -4, -10,   3,   3,  33, -12,
    -27,  -2,  -5,  12,  17,   6,  10, -25,
    -14,  13,   6,  21,  23,  12,  17, -23,
     -6,   7,  26,  31,  65,  56,  25, -20,
     98, 134,  61,  95,  68, 126,  34, -11,
      0,   0,   0,   0,   0,   0,   0,   0,
]
EG_P = [
      0,   0,   0,   0,   0,   0,   0,   0,
     13,   8,   8,  10,  13,   0,   2,  -7,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
     32,  24,  13,   5,  -2,   4,  17,  17,
     94, 100,  85,  67,  56,  53,  82,  84,
    178, 173, 158, 134, 147, 132, 165, 187,
      0,   0,   0,   0,   0,   0,   0,   0,
]
MG_N = [
    -105, -21, -58, -33, -17, -28, -19,  -23,
     -29, -53, -12,  -3,  -1,  18, -14,  -19,
     -23,  -9,  12,  10,  19,  17,  25,  -16,
     -13,   4,  16,  13,  28,  19,  21,   -8,
      -9,  17,  19,  53,  37,  69,  18,   22,
     -47,  60,  37,  65,  84, 129,  73,   44,
     -73, -41,  72,  36,  23,  62,   7,  -17,
    -167, -89, -34, -49,  61, -97, -15, -107,
]
EG_N = [
    -29, -51, -23, -15, -22, -18, -50, -64,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -58, -38, -13, -28, -31, -27, -63, -99,
]
MG_B = [
    -33,  -3, -14, -21, -13, -12, -39, -21,
      4,  15,  16,   0,   7,  21,  33,   1,
      0,  15,  15,  15,  14,  27,  18,  10,
     -6,  13,  13,  26,  34,  12,  10,   4,
     -4,   5,  19,  50,  37,  37,   7,  -2,
    -16,  37,  43,  40,  35,  50,  37,  -2,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -29,   4, -82, -37, -25, -42,   7,  -8,
]
EG_B = [
    -23,  -9, -23,  -5,  -9, -16,  -5, -17,
    -14, -18,  -7,  -1,   4,  -9, -15, -27,
    -12,  -3,   8,  10,  13,   3,  -7, -15,
     -6,   3,  13,  19,   7,  10,  -3,  -9,
     -3,   9,  12,   9,  14,  10,   3,   2,
      2,  -8,   0,  -1,  -2,   6,   0,   4,
     -8,  -4,   7, -12,  -3, -13,  -4, -14,
    -14, -21, -11,  -8,  -7,  -9, -17, -24,
]
MG_R = [
    -19, -13,   1,  17,  16,   7, -37, -26,
    -44, -16, -20,  -9,  -1,  11,  -6, -71,
    -45, -25, -16, -17,   3,   0,  -5, -33,
    -36, -26, -12,  -1,   9,  -7,   6, -23,
    -24, -11,   7,  26,  24,  35,  -8, -20,
     -5,  19,  26,  36,  17,  45,  61,  16,
     27,  32,  58,  62,  80,  67,  26,  44,
     32,  42,  32,  51,  63,   9,  31,  43,
]
EG_R = [
    -9,  2,  3, -1, -5, -13,   4, -20,
    -6, -6,  0,  2, -9,  -9, -11,  -3,
    -4,  0, -5, -1, -7, -12,  -8, -16,
     3,  5,  8,  4, -5,  -6,  -8, -11,
     4,  3, 13,  1,  2,   1,  -1,   2,
     7,  7,  7,  5,  4,  -3,  -5,  -3,
    11, 13, 13, 11, -3,   3,   8,   3,
    13, 10, 18, 15, 12,  12,   8,   5,
]
MG_Q = [
     -1, -18,  -9,  10, -15, -25, -31, -50,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -28,   0,  29,  12,  59,  44,  43,  45,
]
EG_Q = [
    -33, -28, -22, -43,  -5, -32, -20, -41,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -18,  28,  19,  47,  31,  34,  39,  23,
      3,  22,  24,  45,  57,  40,  57,  36,
    -20,   6,   9,  49,  47,  35,  19,   9,
    -17,  20,  32,  41,  58,  25,  30,   0,
     -9,  22,  22,  27,  27,  19,  10,  20,
]
MG_K = [
    -15,  36,  12, -54,   8, -28,  24,  14,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -14, -14, -22, -46, -44, -30, -15, -27,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -17, -20, -12, -27, -30, -25, -14, -36,
     -9,  24,   2, -16, -20,   6,  22, -22,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
    -65,  23,  16, -15, -56, -34,   2,  13,
]
EG_K = [
    -53, -34, -21, -11, -28, -14, -24, -43,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -18,  -4,  21,  24,  27,  23,   9, -11,
     -8,  22,  24,  27,  26,  33,  26,   3,
     10,  17,  23,  15,  20,  45,  44,  13,
    -12,  17,  14,  17,  17,  38,  23,  11,
    -74, -35, -18, -18, -11,  15,   4, -17,
]
MG_TBL = [MG_P, MG_N, MG_B, MG_R, MG_Q, MG_K]
EG_TBL = [EG_P, EG_N, EG_B, EG_R, EG_Q, EG_K]

def _build_pst():
    mg_w = [[0]*128 for _ in range(6)]
    eg_w = [[0]*128 for _ in range(6)]
    mg_b = [[0]*128 for _ in range(6)]
    eg_b = [[0]*128 for _ in range(6)]
    for pt in range(6):
        for s in range(128):
            if s & 0x88: continue
            r = s >> 4; f = s & 7
            iw = r * 8 + f
            ib = (7 - r) * 8 + f
            mg_w[pt][s] = MG_VAL[pt] + MG_TBL[pt][iw]
            eg_w[pt][s] = EG_VAL[pt] + EG_TBL[pt][iw]
            mg_b[pt][s] = MG_VAL[pt] + MG_TBL[pt][ib]
            eg_b[pt][s] = EG_VAL[pt] + EG_TBL[pt][ib]
    return mg_w, eg_w, mg_b, eg_b

MG_W, EG_W, MG_BL, EG_BL = _build_pst()

# 0x88 geometry helpers
def sq(r, f):      return (r << 4) | f
def rank_of(s):    return s >> 4
def file_of(s):    return s & 7
def sq_name(s):    return "abcdefgh"[s & 7] + str((s >> 4) + 1)
def name_sq(n):    return ((int(n[1]) - 1) << 4) | (ord(n[0]) - 97)

# CORRECT knight offsets: (±1,±2) and (±2,±1)
KN_OFS    = (0x12, 0x21, 0x1F, 0x0E, -0x12, -0x21, -0x1F, -0x0E)
KING_OFS  = (0x11, 0x10, 0x0F, 0x01, -0x01, -0x0F, -0x10, -0x11)
BISH_OFS  = (0x11, 0x0F, -0x0F, -0x11)
ROOK_OFS  = (0x10, 0x01, -0x01, -0x10)
QUEEN_OFS = BISH_OFS + ROOK_OFS

# Pre-compute set for fast O(1) knight/king offset lookup
KN_OFS_SET   = set(KN_OFS)
KING_OFS_SET = set(KING_OFS)

# Zobrist keys
_rng = random.Random(0xC0FFEE)
ZOB_PIECE  = {p: [_rng.getrandbits(64) for _ in range(128)] for p in "PNBRQKpnbrqk"}
ZOB_SIDE   = _rng.getrandbits(64)
ZOB_EP     = [_rng.getrandbits(64) for _ in range(128)]
ZOB_CASTLE = {c: _rng.getrandbits(64) for c in "KQkq"}

# Piece values for SEE / MVV-LVA
SEE_VAL = [100, 320, 330, 500, 900, 20000]
MVV     = SEE_VAL  # alias for readability


# ──────────────────────────────────────────────────────────────
#  BOARD
# ──────────────────────────────────────────────────────────────
class Board:
    __slots__ = ("pieces","side","castle","ep","halfmove","fullmove",
                 "kw","kb","hash","_hist","_hash_hist")

    def __init__(self):
        self.pieces   = [None]*128
        self.side     = 'w'
        self.castle   = {'K':False,'Q':False,'k':False,'q':False}
        self.ep       = -1
        self.halfmove = 0
        self.fullmove = 1
        self.kw = -1; self.kb = -1
        self.hash = 0
        self._hist = []
        self._hash_hist = []

    @classmethod
    def from_fen(cls, fen):
        b = cls()
        parts = fen.split()
        for i, row in enumerate(parts[0].split('/')):
            f = 0; r = 7 - i
            for ch in row:
                if ch.isdigit(): f += int(ch)
                else:
                    s = (r << 4) | f
                    b.pieces[s] = ch
                    if   ch == 'K': b.kw = s
                    elif ch == 'k': b.kb = s
                    f += 1
        b.side = parts[1] if len(parts) > 1 else 'w'
        cs = parts[2] if len(parts) > 2 else "-"
        b.castle = {c: (c in cs) for c in "KQkq"}
        b.ep = name_sq(parts[3]) if len(parts) > 3 and parts[3] != '-' else -1
        b.halfmove = int(parts[4]) if len(parts) > 4 else 0
        b.fullmove = int(parts[5]) if len(parts) > 5 else 1
        b._recompute_hash()
        return b

    def _recompute_hash(self):
        h = 0
        for s in range(128):
            if s & 0x88: continue
            p = self.pieces[s]
            if p: h ^= ZOB_PIECE[p][s]
        if self.side == 'b': h ^= ZOB_SIDE
        if self.ep != -1:    h ^= ZOB_EP[self.ep]
        for c, v in self.castle.items():
            if v: h ^= ZOB_CASTLE[c]
        self.hash = h

    # FIX 1: proper 2-fold repetition — count occurrences in history;
    #         stop scanning past irreversible moves (halfmove resets).
    def is_repetition(self):
        h = self.hash
        count = 0
        # Only need to look back as far as the last irreversible move.
        # _hash_hist entries correspond 1-to-1 with _hist entries.
        hist = self._hist
        hash_hist = self._hash_hist
        limit = len(hash_hist)
        for i in range(limit - 1, -1, -1):
            # Stop at irreversible moves (captures / pawn moves reset halfmove)
            rec = hist[i]
            # rec[1] is captured piece, rec[0] is the move tuple
            move_rec = rec[0]
            if move_rec == 'null':
                continue
            if hash_hist[i] == h:
                count += 1
                if count >= 2:
                    return True
            # Check if this move was irreversible
            captured_piece = rec[1]
            moved_piece_flag = move_rec[2] if move_rec != 'null' else None
            # Pawn move or capture = irreversible
            frm_sq = move_rec[0]
            piece_moved = None
            # We can't read board.pieces here (already unmade), so we use
            # halfmove counter baked into history instead.
            old_hm = rec[4]
            if old_hm == 0:
                # halfmove was reset at this ply → irreversible boundary
                break
        return False

    def is_attacked(self, s, by_white):
        pcs = self.pieces
        if by_white:
            t = s - 0x11
            if not (t & 0x88) and pcs[t] == 'P': return True
            t = s - 0x0F
            if not (t & 0x88) and pcs[t] == 'P': return True
            N='N'; K='K'; Q='Q'; R='R'; B='B'
        else:
            t = s + 0x11
            if not (t & 0x88) and pcs[t] == 'p': return True
            t = s + 0x0F
            if not (t & 0x88) and pcs[t] == 'p': return True
            N='n'; K='k'; Q='q'; R='r'; B='b'
        for d in KN_OFS:
            t = s + d
            if not (t & 0x88) and pcs[t] == N: return True
        for d in KING_OFS:
            t = s + d
            if not (t & 0x88) and pcs[t] == K: return True
        for d in BISH_OFS:
            t = s + d
            while not (t & 0x88):
                p = pcs[t]
                if p:
                    if p == B or p == Q: return True
                    break
                t += d
        for d in ROOK_OFS:
            t = s + d
            while not (t & 0x88):
                p = pcs[t]
                if p:
                    if p == R or p == Q: return True
                    break
                t += d
        return False

    def in_check(self, white):
        return self.is_attacked(self.kw if white else self.kb, not white)

    def gen_moves(self, captures_only=False):
        moves = []
        pcs = self.pieces
        white = (self.side == 'w')
        ep = self.ep
        for s in range(128):
            if s & 0x88: continue
            p = pcs[s]
            if not p: continue
            if p.isupper() != white: continue
            up = p.upper()
            if up == 'P':
                direction = 0x10 if white else -0x10
                start_rk  = 1 if white else 6
                promo_rk  = 7 if white else 0
                promos    = ('Q','R','B','N') if white else ('q','r','b','n')
                if not captures_only:
                    t = s + direction
                    if not (t & 0x88) and pcs[t] is None:
                        if (t >> 4) == promo_rk:
                            for pr in promos: moves.append((s, t, pr))
                        else:
                            moves.append((s, t, None))
                            if (s >> 4) == start_rk:
                                t2 = t + direction
                                if pcs[t2] is None:
                                    moves.append((s, t2, None))
                for df in (-1, 1):
                    t = s + direction + df
                    if t & 0x88: continue
                    tp = pcs[t]
                    if tp and (tp.isupper() != white):
                        if (t >> 4) == promo_rk:
                            for pr in promos: moves.append((s, t, pr))
                        else:
                            moves.append((s, t, None))
                    elif t == ep and ep != -1:
                        moves.append((s, t, 'ep'))
            elif up == 'N':
                for d in KN_OFS:
                    t = s + d
                    if t & 0x88: continue
                    tp = pcs[t]
                    if tp and (tp.isupper() == white): continue
                    if captures_only and tp is None: continue
                    moves.append((s, t, None))
            elif up == 'K':
                for d in KING_OFS:
                    t = s + d
                    if t & 0x88: continue
                    tp = pcs[t]
                    if tp and (tp.isupper() == white): continue
                    if captures_only and tp is None: continue
                    moves.append((s, t, None))
                if not captures_only:
                    self._add_castle(moves, white)
            else:
                if up == 'B':   dirs = BISH_OFS
                elif up == 'R': dirs = ROOK_OFS
                else:           dirs = QUEEN_OFS
                for d in dirs:
                    t = s + d
                    while not (t & 0x88):
                        tp = pcs[t]
                        if tp:
                            if tp.isupper() != white:
                                moves.append((s, t, None))
                            break
                        if not captures_only:
                            moves.append((s, t, None))
                        t += d
        return moves

    def _add_castle(self, moves, white):
        pcs = self.pieces
        if white:
            back = 0; ks, qs = 'K', 'Q'; opp_white = False
        else:
            back = 7; ks, qs = 'k', 'q'; opp_white = True
        if self.castle[ks]:
            if (pcs[sq(back,5)] is None and pcs[sq(back,6)] is None and
                not self.is_attacked(sq(back,4), opp_white) and
                not self.is_attacked(sq(back,5), opp_white) and
                not self.is_attacked(sq(back,6), opp_white)):
                moves.append((sq(back,4), sq(back,6), 'ck'))
        if self.castle[qs]:
            if (pcs[sq(back,3)] is None and pcs[sq(back,2)] is None and
                pcs[sq(back,1)] is None and
                not self.is_attacked(sq(back,4), opp_white) and
                not self.is_attacked(sq(back,3), opp_white) and
                not self.is_attacked(sq(back,2), opp_white)):
                moves.append((sq(back,4), sq(back,2), 'cq'))

    def make_move(self, move):
        frm, to, flag = move
        pcs = self.pieces
        piece    = pcs[frm]
        captured = pcs[to]
        old_ep   = self.ep
        old_castle = self.castle.copy()
        old_hm   = self.halfmove
        old_hash = self.hash

        h = self.hash
        if old_ep != -1: h ^= ZOB_EP[old_ep]
        h ^= ZOB_PIECE[piece][frm]
        pcs[frm] = None

        if flag == 'ep':
            cap_sq = to - 0x10 if self.side == 'w' else to + 0x10
            captured = pcs[cap_sq]
            h ^= ZOB_PIECE[captured][cap_sq]
            pcs[cap_sq] = None
        elif captured:
            h ^= ZOB_PIECE[captured][to]

        # Store history AFTER resolving the actual captured piece (ep fix)
        self._hist.append((move, captured, old_ep, old_castle, old_hm, old_hash))

        # FIX 10: handle both upper and lower-case promotion flags safely
        if flag and flag not in ('ck','cq','ep'):
            new_p = flag  # already correct case (set in gen_moves)
            h ^= ZOB_PIECE[new_p][to]
            pcs[to] = new_p
        else:
            h ^= ZOB_PIECE[piece][to]
            pcs[to] = piece

        if flag == 'ck':
            back = 0 if self.side == 'w' else 7
            rook = pcs[sq(back,7)]
            h ^= ZOB_PIECE[rook][sq(back,7)]
            h ^= ZOB_PIECE[rook][sq(back,5)]
            pcs[sq(back,5)] = rook
            pcs[sq(back,7)] = None
        elif flag == 'cq':
            back = 0 if self.side == 'w' else 7
            rook = pcs[sq(back,0)]
            h ^= ZOB_PIECE[rook][sq(back,0)]
            h ^= ZOB_PIECE[rook][sq(back,3)]
            pcs[sq(back,3)] = rook
            pcs[sq(back,0)] = None

        if piece == 'K': self.kw = to
        elif piece == 'k': self.kb = to

        self.ep = -1
        if piece == 'P' and (to - frm) == 0x20:
            # Only set ep if an enemy pawn can actually capture it (FIX 9)
            ep_sq = frm + 0x10
            ep_file = file_of(ep_sq)
            valid_ep = False
            if ep_file > 0 and pcs[ep_sq - 1] == 'p': valid_ep = True
            if ep_file < 7 and pcs[ep_sq + 1] == 'p': valid_ep = True
            if valid_ep:
                self.ep = ep_sq; h ^= ZOB_EP[self.ep]
        elif piece == 'p' and (frm - to) == 0x20:
            ep_sq = frm - 0x10
            ep_file = file_of(ep_sq)
            valid_ep = False
            if ep_file > 0 and pcs[ep_sq - 1] == 'P': valid_ep = True
            if ep_file < 7 and pcs[ep_sq + 1] == 'P': valid_ep = True
            if valid_ep:
                self.ep = ep_sq; h ^= ZOB_EP[self.ep]

        castle = self.castle
        if piece == 'K':
            if castle['K']: h ^= ZOB_CASTLE['K']; castle['K'] = False
            if castle['Q']: h ^= ZOB_CASTLE['Q']; castle['Q'] = False
        elif piece == 'k':
            if castle['k']: h ^= ZOB_CASTLE['k']; castle['k'] = False
            if castle['q']: h ^= ZOB_CASTLE['q']; castle['q'] = False
        for csq, right in ((0x00,'Q'),(0x07,'K'),(0x70,'q'),(0x77,'k')):
            if (frm == csq or to == csq) and castle[right]:
                h ^= ZOB_CASTLE[right]; castle[right] = False

        if piece.upper() == 'P' or captured:
            self.halfmove = 0
        else:
            self.halfmove += 1
        if self.side == 'b': self.fullmove += 1
        self.side = 'b' if self.side == 'w' else 'w'
        h ^= ZOB_SIDE
        self.hash = h
        self._hash_hist.append(h)

    def unmake_move(self):
        move, captured, old_ep, old_castle, old_hm, old_hash = self._hist.pop()
        self._hash_hist.pop()
        frm, to, flag = move
        pcs = self.pieces
        self.side = 'b' if self.side == 'w' else 'w'
        if self.side == 'b': self.fullmove -= 1

        # FIX 10: restore the pawn correctly for any case of promotion flag
        if flag and flag not in ('ck','cq','ep'):
            moved = 'P' if self.side == 'w' else 'p'
        else:
            moved = pcs[to]
        pcs[frm] = moved

        if flag == 'ep':
            pcs[to] = None
            cap_sq = to - 0x10 if self.side == 'w' else to + 0x10
            pcs[cap_sq] = captured
        else:
            pcs[to] = captured

        if flag == 'ck':
            back = 0 if self.side == 'w' else 7
            rook = pcs[sq(back,5)]
            pcs[sq(back,7)] = rook; pcs[sq(back,5)] = None
        elif flag == 'cq':
            back = 0 if self.side == 'w' else 7
            rook = pcs[sq(back,3)]
            pcs[sq(back,0)] = rook; pcs[sq(back,3)] = None

        if moved == 'K': self.kw = frm
        elif moved == 'k': self.kb = frm
        self.ep = old_ep
        self.castle = old_castle
        self.halfmove = old_hm
        self.hash = old_hash

    def make_null(self):
        old_ep = self.ep
        self._hist.append(('null', None, old_ep, self.castle.copy(),
                           self.halfmove, self.hash))
        h = self.hash
        if old_ep != -1: h ^= ZOB_EP[old_ep]
        self.ep = -1; self.halfmove += 1
        self.side = 'b' if self.side == 'w' else 'w'
        h ^= ZOB_SIDE
        self.hash = h
        self._hash_hist.append(h)

    def unmake_null(self):
        _, _, old_ep, old_castle, old_hm, old_hash = self._hist.pop()
        self._hash_hist.pop()
        self.side = 'b' if self.side == 'w' else 'w'
        self.ep = old_ep
        self.castle = old_castle
        self.halfmove = old_hm
        self.hash = old_hash

    def move_to_uci(self, m):
        frm, to, flag = m
        s = sq_name(frm) + sq_name(to)
        if flag and flag not in ('ck','cq','ep'):
            s += flag.lower()
        return s

    def uci_to_move(self, uci):
        frm = name_sq(uci[:2]); to = name_sq(uci[2:4]); flag = None
        piece = self.pieces[frm]
        if len(uci) == 5:
            flag = uci[4].upper() if (piece and piece.isupper()) else uci[4].lower()
        elif piece and piece.upper() == 'K' and abs(file_of(to)-file_of(frm)) == 2:
            flag = 'ck' if file_of(to) == 6 else 'cq'
        elif piece and piece.upper() == 'P' and to == self.ep and self.ep != -1:
            flag = 'ep'
        return (frm, to, flag)

    def side_has_non_pawn(self, white):
        pcs = self.pieces
        for s in range(128):
            if s & 0x88: continue
            p = pcs[s]
            if not p: continue
            if p.isupper() == white and p.upper() in ('N','B','R','Q'):
                return True
        return False


# ──────────────────────────────────────────────────────────────
#  STATIC EXCHANGE EVALUATION (SEE)  — FIX 4: build occ once
# ──────────────────────────────────────────────────────────────
def see(board, frm, to):
    """
    Returns the material gain/loss of the capture frm->to.
    Positive = winning, negative = losing.
    """
    pcs = board.pieces
    target = pcs[to]
    if target is None:
        return 0
    gain = [0] * 32
    gain[0] = SEE_VAL[PIECE_IDX[target]]

    # Build occupancy once (FIX 4)
    occ = set()
    for s in range(128):
        if not (s & 0x88) and pcs[s]:
            occ.add(s)

    attacker = pcs[frm]
    occ.discard(frm)
    side_white = attacker.isupper()
    d = 1

    while True:
        gain[d] = SEE_VAL[PIECE_IDX[attacker]] - gain[d-1]
        side_white = not side_white
        best_val = INF
        best_sq  = -1
        for s in occ:
            p = pcs[s]
            if not p or p.isupper() != side_white: continue
            pv = SEE_VAL[PIECE_IDX[p]]
            if pv >= best_val: continue
            up = p.upper()
            attacks = False
            if up == 'P':
                if side_white:
                    if to == s + 0x11 or to == s + 0x0F: attacks = True
                else:
                    if to == s - 0x11 or to == s - 0x0F: attacks = True
            elif up == 'N':
                if (to - s) in KN_OFS_SET: attacks = True
            elif up == 'K':
                if (to - s) in KING_OFS_SET: attacks = True
            else:  # B, R, Q
                if up in ('B', 'Q'):
                    for d2 in BISH_OFS:
                        t = s + d2
                        while not (t & 0x88):
                            if t == to: attacks = True; break
                            if t in occ: break
                            t += d2
                        if attacks: break
                if not attacks and up in ('R', 'Q'):
                    for d2 in ROOK_OFS:
                        t = s + d2
                        while not (t & 0x88):
                            if t == to: attacks = True; break
                            if t in occ: break
                            t += d2
                        if attacks: break
            if attacks:
                best_val = pv
                best_sq  = s
        if best_sq == -1:
            break
        attacker = pcs[best_sq]
        occ.discard(best_sq)
        d += 1

    while d > 1:
        d -= 1
        gain[d-1] = -max(-gain[d-1], gain[d])
    return gain[0]


# ──────────────────────────────────────────────────────────────
#  EVALUATION
# ──────────────────────────────────────────────────────────────
def evaluate(board):
    pcs = board.pieces
    mg_w = mg_b = eg_w = eg_b = 0
    phase = 0
    wpawn_files = 0; bpawn_files = 0
    wpawns = []; bpawns = []
    wbishops = 0; bbishops = 0
    wrooks  = []; brooks = []
    for s in range(128):
        if s & 0x88: continue
        p = pcs[s]
        if not p: continue
        pt = PIECE_IDX[p]
        if p.isupper():
            mg_w += MG_W[pt][s]; eg_w += EG_W[pt][s]
            if pt == 0:
                wpawn_files |= 1 << (s & 7); wpawns.append(s)
            elif pt == 2: wbishops += 1
            elif pt == 3: wrooks.append(s)
        else:
            mg_b += MG_BL[pt][s]; eg_b += EG_BL[pt][s]
            if pt == 0:
                bpawn_files |= 1 << (s & 7); bpawns.append(s)
            elif pt == 2: bbishops += 1
            elif pt == 3: brooks.append(s)
        phase += PHASE_INC[pt]

    if wbishops >= 2: mg_w += 30; eg_w += 50
    if bbishops >= 2: mg_b += 30; eg_b += 50

    for f in range(8):
        wc = sum(1 for s in wpawns if (s & 7) == f)
        bc = sum(1 for s in bpawns if (s & 7) == f)
        if wc > 1: mg_w -= 12*(wc-1); eg_w -= 20*(wc-1)
        if bc > 1: mg_b -= 12*(bc-1); eg_b -= 20*(bc-1)
        nb = 0
        if f > 0: nb |= 1 << (f-1)
        if f < 7: nb |= 1 << (f+1)
        if wc and not (wpawn_files & nb): mg_w -= 12; eg_w -= 18
        if bc and not (bpawn_files & nb): mg_b -= 12; eg_b -= 18

    for r in wrooks:
        fm = 1 << (r & 7)
        if not (wpawn_files & fm):
            if not (bpawn_files & fm): mg_w += 25; eg_w += 15
            else: mg_w += 12; eg_w += 8
    for r in brooks:
        fm = 1 << (r & 7)
        if not (bpawn_files & fm):
            if not (wpawn_files & fm): mg_b += 25; eg_b += 15
            else: mg_b += 12; eg_b += 8

    mg = mg_w - mg_b; eg = eg_w - eg_b
    mg_phase = phase if phase < TOTAL_PHASE else TOTAL_PHASE
    eg_phase = TOTAL_PHASE - mg_phase
    score = (mg * mg_phase + eg * eg_phase) // TOTAL_PHASE
    score += 10 if board.side == 'w' else -10
    return score if board.side == 'w' else -score


# ──────────────────────────────────────────────────────────────
#  TRANSPOSITION TABLE  — FIX 3: O(1) eviction via victim pool
# ──────────────────────────────────────────────────────────────
TT_EXACT, TT_LOWER, TT_UPPER = 0, 1, 2
TT: dict = {}
TT_MAX  = 1 << 20
_tt_age = 0
# Small ring of keys to evict (avoids full-dict scan on overflow)
_tt_victims: list = []
_TT_VICTIM_CAP = 256

def tt_store(key, depth, flag, score, move, ply):
    if score >=  MATE_BOUND: score += ply
    elif score <= -MATE_BOUND: score -= ply
    existing = TT.get(key)
    if existing is not None:
        # Replace only if new search is deeper or entry is stale
        if existing[0] > depth and existing[4] == _tt_age:
            return
    if len(TT) >= TT_MAX:
        # FIX 3: O(1) eviction — rotate through a victim pool
        global _tt_victims
        if _tt_victims:
            victim = _tt_victims.pop()
            TT.pop(victim, None)
        else:
            # Refill victim pool from stale entries first, else any entry
            _tt_victims = [k for k, v in list(TT.items())[:512] if v[4] != _tt_age]
            if not _tt_victims:
                _tt_victims = list(TT.keys())[:512]
            TT.pop(_tt_victims.pop(), None)
    TT[key] = (depth, flag, score, move, _tt_age)

def tt_probe(key, ply):
    e = TT.get(key)
    if not e: return None
    d, f, s, m, _age = e
    if s >=  MATE_BOUND: s -= ply
    elif s <= -MATE_BOUND: s += ply
    return d, f, s, m


# ──────────────────────────────────────────────────────────────
#  MOVE ORDERING
# ──────────────────────────────────────────────────────────────
killers    = [[None, None] for _ in range(MAX_PLY)]
history: dict = {}
countermov: dict = {}

def order_moves(board, moves, tt_move, ply, prev):
    cm = countermov.get(prev) if prev else None
    k1 = killers[ply][0]; k2 = killers[ply][1]
    pcs = board.pieces
    scored = []
    for m in moves:
        if m == tt_move:
            s = 10_000_000
        else:
            frm, to, flag = m
            cap = pcs[to]
            is_promo = bool(flag and flag not in ('ck','cq','ep'))
            if cap or flag == 'ep' or is_promo:
                if is_promo:
                    s = 1_900_000 + MVV[PIECE_IDX[flag]]
                    if cap: s += MVV[PIECE_IDX[cap]]
                else:
                    see_score = see(board, frm, to) if cap else 0
                    if see_score >= 0:
                        s = 1_000_000 + see_score
                    else:
                        s = 500_000 + see_score
            elif m == k1: s = 900_000
            elif m == k2: s = 800_000
            elif m == cm: s = 700_000
            else:
                piece = pcs[frm]
                s = history.get((piece, to), 0) if piece else 0
        scored.append((s, m))
    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored]


# ──────────────────────────────────────────────────────────────
#  SEARCH
# ──────────────────────────────────────────────────────────────
nodes = 0
start_time = 0.0
stop_flag = False

def time_up():
    # FIX 8: check every 4095 nodes to reduce perf_counter overhead
    return (time.perf_counter() - start_time) > TIME_LIMIT

def quiesce(board, alpha, beta, ply):
    global nodes, stop_flag
    nodes += 1
    # FIX 8: raised interval to 4095
    if nodes & 4095 == 0 and time_up():
        stop_flag = True
        return alpha

    stand = evaluate(board)
    if stand >= beta: return beta
    if stand + 975 < alpha: return alpha   # delta pruning
    if stand > alpha: alpha = stand

    moves = board.gen_moves(captures_only=True)

    def _s(m):
        cap = board.pieces[m[1]]
        f   = m[2]
        if f and f not in ('ck','cq','ep'):
            return 900_000 + MVV[PIECE_IDX[f]]
        if cap:
            return see(board, m[0], m[1])
        return 0
    moves.sort(key=_s, reverse=True)

    white = (board.side == 'w')
    for mv in moves:
        frm, to, flag = mv
        cap = board.pieces[to]
        if cap and flag not in ('ck','cq','ep'):
            if see(board, frm, to) < 0:
                continue
        board.make_move(mv)
        if board.in_check(white):
            board.unmake_move(); continue
        score = -quiesce(board, -beta, -alpha, ply + 1)
        board.unmake_move()
        if stop_flag: return alpha
        if score >= beta: return beta
        if score > alpha: alpha = score
    return alpha


def negamax(board, depth, alpha, beta, ply, do_null, prev):
    global nodes, stop_flag
    nodes += 1
    # FIX 8: raised interval to 4095
    if nodes & 4095 == 0 and time_up():
        stop_flag = True
        return 0

    if ply > 0 and board.halfmove >= 100:
        return 0

    if ply > 0 and board.is_repetition():
        return 0

    alpha = max(alpha, -MATE + ply)
    beta  = min(beta,   MATE - ply - 1)
    if alpha >= beta:
        return alpha

    white    = (board.side == 'w')
    in_check = board.in_check(white)
    if in_check:
        depth += 1

    key = board.hash
    tt_move = None
    h = tt_probe(key, ply)
    if h:
        td, tf, ts, tm = h
        tt_move = tm
        if ply > 0 and td >= depth:
            if tf == TT_EXACT: return ts
            elif tf == TT_LOWER and ts >= beta: return ts
            elif tf == TT_UPPER and ts <= alpha: return ts

    if depth <= 0:
        return quiesce(board, alpha, beta, ply)

    static = evaluate(board)

    # Reverse futility pruning
    if not in_check and depth < 7 and abs(beta) < MATE_BOUND:
        if static - 85 * depth >= beta:
            return static - 85 * depth

    # Razoring
    if not in_check and depth <= 2 and static + 300 * depth <= alpha:
        q = quiesce(board, alpha, beta, ply)
        if q <= alpha:
            return q

    # Null-move pruning
    if (do_null and not in_check and depth >= 3 and static >= beta
            and board.side_has_non_pawn(white) and abs(beta) < MATE_BOUND):
        R = 2 + depth // 4
        board.make_null()
        score = -negamax(board, depth - 1 - R, -beta, -beta + 1,
                         ply + 1, False, None)
        board.unmake_null()
        if stop_flag: return 0
        if score >= beta:
            return beta if score >= MATE_BOUND else score

    pseudo  = board.gen_moves()
    ordered = order_moves(board, pseudo, tt_move, min(ply, MAX_PLY - 1), prev)

    best_score = -INF
    best_move  = None
    orig_alpha = alpha
    searched   = 0

    for mv in ordered:
        frm, to, flag = mv
        # Read piece BEFORE make_move (FIX 5 — explicit and safe)
        moving_piece = board.pieces[frm]

        is_cap   = board.pieces[to] is not None or flag == 'ep'
        is_promo = bool(flag and flag not in ('ck','cq','ep'))
        is_quiet = not is_cap and not is_promo

        # FIX 6: futility and LMP only after the first legal move is searched
        if searched > 0:
            # Futility pruning
            if (depth <= 3 and not in_check and is_quiet
                    and abs(alpha) < MATE_BOUND):
                if static + 100 + 80 * depth <= alpha:
                    continue
            # Late-move pruning
            if (depth <= 4 and not in_check and is_quiet
                    and searched >= 3 + depth * depth):
                continue
            # SEE pruning for bad captures at low depth
            if (depth <= 6 and not in_check and is_cap and not is_promo
                    and abs(alpha) < MATE_BOUND):
                if see(board, frm, to) < -50 * depth:
                    continue

        board.make_move(mv)
        if board.in_check(white):
            board.unmake_move(); continue
        gives_check = board.in_check(not white)

        reduction = 0
        if (depth >= 3 and searched >= 2 and is_quiet
                and not in_check and not gives_check):
            reduction = 1
            if searched >= 6:  reduction = 2
            if depth >= 6 and searched >= 10: reduction = depth // 3

        if searched == 0:
            score = -negamax(board, depth - 1, -beta, -alpha,
                             ply + 1, True, mv)
        else:
            score = -negamax(board, depth - 1 - reduction, -alpha - 1, -alpha,
                             ply + 1, True, mv)
            if reduction and score > alpha and not stop_flag:
                score = -negamax(board, depth - 1, -alpha - 1, -alpha,
                                 ply + 1, True, mv)
            if alpha < score < beta and not stop_flag:
                score = -negamax(board, depth - 1, -beta, -alpha,
                                 ply + 1, True, mv)

        board.unmake_move()
        if stop_flag:
            return best_score if best_move else alpha

        searched += 1
        if score > best_score:
            best_score = score
            best_move  = mv
            if score > alpha:
                alpha = score
                if alpha >= beta:
                    if is_quiet and moving_piece:
                        if killers[min(ply, MAX_PLY-1)][0] != mv:
                            killers[min(ply, MAX_PLY-1)][1] = killers[min(ply, MAX_PLY-1)][0]
                            killers[min(ply, MAX_PLY-1)][0] = mv
                        k = (moving_piece, to)
                        # FIX 2: cap history to avoid unbounded growth
                        history[k] = min(history.get(k, 0) + depth * depth, 32_000)
                        if prev: countermov[prev] = mv
                    break

    if searched == 0:
        return -(MATE - ply) if in_check else 0

    if best_move:
        if best_score <= orig_alpha: f = TT_UPPER
        elif best_score >= beta:     f = TT_LOWER
        else:                        f = TT_EXACT
        tt_store(key, depth, f, best_score, best_move, ply)
    return best_score


# ──────────────────────────────────────────────────────────────
#  OPENING BOOK  (FIX 9: ep key normalised)
# ──────────────────────────────────────────────────────────────
BOOK = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -":
        ["e2e4","d2d4","g1f3","c2c4"],
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -":
        ["c7c5","e7e5","e7e6","c7c6","g8f6","d7d5"],
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -":
        ["g8f6","d7d5","e7e6","f7f5"],
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -":
        ["d7d5","g8f6","c7c5","e7e6"],
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq -":
        ["e7e5","g8f6","c7c5","e7e6"],
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -":
        ["g1f3","f1c4","b1c3","f2f4"],
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -":
        ["b8c6","g8f6","d7d6","f7f5"],
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -":
        ["f1b5","f1c4","d2d4","b1c3"],
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -":
        ["a7a6","g8f6","f8c5","d7d6"],
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq -":
        ["f8c5","g8f6","f7f5","d7d6"],
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -":
        ["g1f3","b1c3","c2c3","f2f4"],
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -":
        ["d7d6","b8c6","e7e6","g8f6"],
    "rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -":
        ["d2d4","f1b5","b1c3","c2c3"],
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -":
        ["d2d4","b1c3","g1f3"],
    "rnbqkbnr/pppp1ppp/4p3/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq -":
        ["d7d5","b8c6","g8f6"],
    "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -":
        ["d2d4","b1c3","g1f3"],
    "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq -":
        ["c2c4","g1f3","b1c3"],
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq -":
        ["e7e6","c7c6","d5c4","g8f6"],
    "rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -":
        ["b1c3","g1f3","e2e3"],
    "rnbqkbnr/ppp1pppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq -":
        ["e2e4","g1f3","e2e3"],
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq -":
        ["c2c4","g1f3","c1g5"],
    "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -":
        ["b1c3","e2e4","g1f3"],
    "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq -":
        ["d1c2","e2e3","g1f3","a2a3"],
    "rnbqkbnr/pppp1ppp/8/4p3/4PP2/8/PPPP2PP/RNBQKBNR b KQkq -":
        ["f7f6","d7d5","f8c5","g8f6"],
}

def board_to_book_key(board):
    """Generate book key. FIX 9: ep included only when a capture is possible."""
    rows = []
    for r in range(7, -1, -1):
        empty = 0; row = ""
        for f in range(8):
            p = board.pieces[(r<<4)|f]
            if p is None: empty += 1
            else:
                if empty: row += str(empty); empty = 0
                row += p
        if empty: row += str(empty)
        rows.append(row)
    placement = "/".join(rows)
    cs = "".join(c for c in "KQkq" if board.castle[c]) or "-"
    # Only include ep square if it's actually set (board.make_move already
    # validates that an enemy pawn can capture it)
    ep = sq_name(board.ep) if board.ep != -1 else "-"
    return f"{placement} {board.side} {cs} {ep}"

def _legal(board, mv, white):
    board.make_move(mv)
    ok = not board.in_check(white)
    board.unmake_move()
    return ok

def book_lookup(board):
    key = board_to_book_key(board)
    ucis = BOOK.get(key)
    if not ucis: return None
    white = (board.side == 'w')
    candidates = list(ucis)
    random.shuffle(candidates)
    for u in candidates:
        try:
            mv = board.uci_to_move(u)
        except Exception:
            continue
        if mv[0] < 0 or mv[0] > 127 or (mv[0] & 0x88): continue
        if mv[1] < 0 or mv[1] > 127 or (mv[1] & 0x88): continue
        if board.pieces[mv[0]] is None: continue
        if _legal(board, mv, white):
            return mv
    return None


# ──────────────────────────────────────────────────────────────
#  ROOT SEARCH
# ──────────────────────────────────────────────────────────────
def search(board):
    global nodes, start_time, stop_flag, killers, history, countermov
    global _tt_age, _tt_victims

    bm = book_lookup(board)
    if bm is not None:
        return bm

    start_time = time.perf_counter()
    nodes      = 0
    stop_flag  = False
    killers    = [[None, None] for _ in range(MAX_PLY)]
    # FIX 2: decay history at start of each search (halve all values)
    history    = {k: v >> 1 for k, v in history.items()}
    countermov = {}
    _tt_age   += 1
    _tt_victims = []

    white = (board.side == 'w')
    legal_root = [m for m in board.gen_moves() if _legal(board, m, white)]
    if not legal_root:
        return None
    best_move  = legal_root[0]
    prev_score = 0

    for depth in range(1, 64):
        if time.perf_counter() - start_time > SOFT_LIMIT:
            break
        if depth >= 4:
            window = 40
            alpha = prev_score - window; beta = prev_score + window
        else:
            window = INF; alpha, beta = -INF, INF
        while True:
            score = negamax(board, depth, alpha, beta, 0, True, None)
            if stop_flag: break
            if score <= alpha:
                alpha = max(-INF, alpha - window * 2); window *= 2
            elif score >= beta:
                beta = min(INF, beta + window * 2); window *= 2
            else:
                break
            if time_up(): stop_flag = True; break
        if stop_flag: break
        e = TT.get(board.hash)
        if e and e[3] is not None:
            best_move  = e[3]
            prev_score = score
        if abs(prev_score) >= MATE_BOUND:
            break

    return best_move


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────
DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def next_move(fen: str) -> str:
    """
    Hackathon-compatible entry point.
    Input:  FEN string (e.g. "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    Output: UCI move string (e.g. "e7e5") or None if no legal move
    """
    try:
        # Validate FEN with python-chess first
        chess_board = chess.Board(fen)
    except Exception:
        fen = DEFAULT_FEN
        chess_board = chess.Board(fen)

    legal_uci_set = {m.uci() for m in chess_board.legal_moves}

    if not legal_uci_set:
        return None

    # Try our custom engine first
    try:
        board = Board.from_fen(fen)
        mv = search(board)
        if mv is not None:
            uci_str = board.move_to_uci(mv)
            # Validate against python-chess to ensure legality
            if uci_str in legal_uci_set:
                return uci_str
    except Exception:
        pass

    # Fallback: pick best move from python-chess legal moves using simple eval
    best_move = None
    best_score = -999999
    for legal_move in chess_board.legal_moves:
        chess_board.push(legal_move)
        # Simple material evaluation as fallback
        score = 0
        piece_vals = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0}
        for sq_idx in chess.SQUARES:
            piece = chess_board.piece_at(sq_idx)
            if piece:
                val = piece_vals.get(piece.symbol().upper(), 0)
                if piece.color == chess_board.turn:
                    score += val
                else:
                    score -= val
        score = -score  # Negate because we pushed the move (now opponent's turn)
        if chess_board.is_checkmate():
            score = 99999
        chess_board.pop()
        if score > best_score:
            best_score = score
            best_move = legal_move

    return str(best_move) if best_move else str(list(chess_board.legal_moves)[0])


def main():
    if len(sys.argv) > 1:
        fen = " ".join(sys.argv[1:])
    else:
        data = sys.stdin.read().strip()
        fen = data if data else DEFAULT_FEN
    result = next_move(fen)
    print(result if result else "(none)")


if __name__ == "__main__":
    main()