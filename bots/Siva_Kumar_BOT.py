import sys
import time
import random
import argparse

# --- CONSTANTS (Finalized for Submission) ---
WHITE, BLACK = 0, 1
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(6)
PIECE_CHARS = "PNBRQK"

# Full Square Definitions
(A1, B1, C1, D1, E1, F1, G1, H1,
 A2, B2, C2, D2, E2, F2, G2, H2,
 A3, B3, C3, D3, E3, F3, G3, H3,
 A4, B4, C4, D4, E4, F4, G4, H4,
 A5, B5, C5, D5, E5, F5, G5, H5,
 A6, B6, C6, D6, E6, F6, G6, H6,
 A7, B7, C7, D7, E7, F7, G7, H7,
 A8, B8, C8, D8, E8, F8, G8, H8) = range(64)

SQUARE_NAMES = [
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
]

UNIVERSE = 0xFFFFFFFFFFFFFFFF
FILE_A = 0x0101010101010101
FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H = [FILE_A << i for i in range(1, 8)]
RANK_1 = 0x00000000000000FF
RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8 = [RANK_1 << (8 * i) for i in range(1, 8)]
FILE_MASKS = [FILE_A << i for i in range(8)]
NOT_A_FILE, NOT_H_FILE = ~FILE_A & UNIVERSE, ~FILE_H & UNIVERSE

# Move Flags
FLAG_QUIET, FLAG_DOUBLE_PUSH, FLAG_KING_CASTLE, FLAG_QUEEN_CASTLE = 0, 1, 2, 3
FLAG_CAPTURE, FLAG_EP_CAPTURE = 4, 5
FLAG_PROMOTION_N, FLAG_PROMOTION_B, FLAG_PROMOTION_R, FLAG_PROMOTION_Q = 8, 9, 10, 11
FLAG_PROM_CAP_N, FLAG_PROM_CAP_B, FLAG_PROM_CAP_R, FLAG_PROM_CAP_Q = 12, 13, 14, 15
CAPTURE_FLAG_MASK, PROMOTION_FLAG_MASK = 0b0100, 0b1000

# Castling Rights
CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ = 1, 2, 4, 8

# --- BITBOARD UTILITIES ---
def set_bit(bb, sq): return bb | (1 << sq)
def clear_bit(bb, sq): return bb & ~(1 << sq)
def get_bit(bb, sq): return bb & (1 << sq)
def popcount(bb): return bin(bb).count('1')
def lsb(bb): return (bb & -bb).bit_length() - 1
def msb(bb): return bb.bit_length() - 1
def iter_bits(bb):
    while bb:
        l = bb & -bb
        yield l.bit_length() - 1
        bb ^= l

KNIGHT_ATTACKS, KING_ATTACKS = [0]*64, [0]*64
PAWN_ATTACKS, RAY_ATTACKS = [[0]*64 for _ in range(2)], [[0]*64 for _ in range(8)]
DIR_N, DIR_E, DIR_S, DIR_W, DIR_NE, DIR_NW, DIR_SE, DIR_SW = range(8)

def _init_attacks():
    k_offs = [15, 17, 6, 10, -15, -17, -6, -10]
    kg_offs = [8, -8, 1, -1, 9, 7, -9, -7]
    for sq in range(64):
        f, r = sq % 8, sq // 8
        ka, kga = 0, 0
        for o in k_offs:
            t = sq + o
            if 0 <= t < 64:
                tf = t % 8
                if abs(f - tf) <= 2: ka |= (1 << t)
        KNIGHT_ATTACKS[sq] = ka
        for o in kg_offs:
            t = sq + o
            if 0 <= t < 64:
                tf = t % 8
                if abs(f - tf) <= 1: kga |= (1 << t)
        KING_ATTACKS[sq] = kga
        if sq < 56:
            if f > 0: PAWN_ATTACKS[WHITE][sq] |= (1 << (sq + 7))
            if f < 7: PAWN_ATTACKS[WHITE][sq] |= (1 << (sq + 9))
        if sq > 7:
            if f > 0: PAWN_ATTACKS[BLACK][sq] |= (1 << (sq - 9))
            if f < 7: PAWN_ATTACKS[BLACK][sq] |= (1 << (sq - 7))
        for d, (df, dr) in enumerate([(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]):
            ray, nf, nr = 0, f + df, r + dr
            while 0 <= nf < 8 and 0 <= nr < 8:
                ray |= (1 << (nr * 8 + nf))
                nf += df; nr += dr
            RAY_ATTACKS[d][sq] = ray
_init_attacks()

def get_slider_attacks(sq, blockers, pos, neg):
    atk = 0
    for d in pos:
        r = RAY_ATTACKS[d][sq]; b = r & blockers
        atk |= (r ^ RAY_ATTACKS[d][lsb(b)]) if b else r
    for d in neg:
        r = RAY_ATTACKS[d][sq]; b = r & blockers
        atk |= (r ^ RAY_ATTACKS[d][msb(b)]) if b else r
    return atk

def get_bishop_atk(sq, blk): return get_slider_attacks(sq, blk, [DIR_NE, DIR_NW], [DIR_SE, DIR_SW])
def get_rook_atk(sq, blk): return get_slider_attacks(sq, blk, [DIR_N, DIR_E], [DIR_S, DIR_W])
def get_queen_atk(sq, blk): return get_bishop_atk(sq, blk) | get_rook_atk(sq, blk)

def encode_move(f, t, flag=0): return f | (t << 6) | (flag << 12)
def move_from(m): return m & 0x3F
def move_to(m): return (m >> 6) & 0x3F
def move_flag(m): return (m >> 12) & 0x0F
def move_to_uci(m):
    if m == 0: return "0000"
    f, t, fl = move_from(m), move_to(m), move_flag(m)
    res = SQUARE_NAMES[f] + SQUARE_NAMES[t]
    if fl & PROMOTION_FLAG_MASK: res += " nbrq"[fl & 0x3]
    return res

# --- BOARD ---
random.seed(42)
ZOBRIST_PIECES = [[[random.getrandbits(64) for _ in range(64)] for _ in range(6)] for _ in range(2)]
ZOBRIST_SIDE, ZOBRIST_CASTLE, ZOBRIST_EP = random.getrandbits(64), [random.getrandbits(64) for _ in range(16)], [random.getrandbits(64) for _ in range(8)]

class Board:
    def __init__(self): self.pieces, self.colors, self.all_pieces, self.side, self.castle, self.ep, self.halfmove, self.fullmove, self.key, self.stack = [[0]*6 for _ in range(2)], [0, 0], 0, WHITE, 0, -1, 0, 1, 0, []
    def load_fen(self, fen):
        try:
            parts = fen.split()
            if len(parts) < 6: fen += " - 0 1"
            p, s, c, e, hm, fm = parts[:6]
            self.pieces, self.colors, sq = [[0]*6 for _ in range(2)], [0, 0], 56
            for char in p:
                if char == '/': sq -= 16
                elif char.isdigit(): sq += int(char)
                else:
                    col = WHITE if char.isupper() else BLACK; pt = PIECE_CHARS.find(char.upper())
                    self.pieces[col][pt] = set_bit(self.pieces[col][pt], sq); self.colors[col] = set_bit(self.colors[col], sq); sq += 1
            self.all_pieces, self.side, self.castle = (self.colors[0] | self.colors[1]), (WHITE if s == 'w' else BLACK), 0
            for char, mask in zip('KQkq', [1, 2, 4, 8]):
                if char in c: self.castle |= mask
            self.ep = (ord(e[0])-'a') + (int(e[1])-1)*8 if e != '-' else -1
            self.halfmove, self.fullmove, self.key = int(hm), int(fm), self.gen_key()
        except: self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    def gen_key(self):
        k = 0
        for c in range(2):
            for p in range(6):
                for sq in iter_bits(self.pieces[c][p]): k ^= ZOBRIST_PIECES[c][p][sq]
        if self.side == BLACK: k ^= ZOBRIST_SIDE
        k ^= ZOBRIST_CASTLE[self.castle]
        if self.ep != -1: k ^= ZOBRIST_EP[self.ep % 8]
        return k
    def get_piece(self, sq):
        for p in range(6):
            if get_bit(self.pieces[0][p] | self.pieces[1][p], sq): return p
        return -1
    def make_move(self, m):
        f, t, fl, us, them = move_from(m), move_to(m), move_flag(m), self.side, 1-self.side
        p, cap = self.get_piece(f), -1; self.stack.append((self.key, self.castle, self.ep, self.halfmove, cap))
        if self.ep != -1: self.key ^= ZOBRIST_EP[self.ep % 8]
        self.key ^= ZOBRIST_CASTLE[self.castle]
        self.pieces[us][p] = clear_bit(self.pieces[us][p], f); self.colors[us] = clear_bit(self.colors[us], f); self.key ^= ZOBRIST_PIECES[us][p][f]
        if fl & CAPTURE_FLAG_MASK:
            if fl == FLAG_EP_CAPTURE: cap = PAWN; cs = t - 8 if us == WHITE else t + 8
            else: cap, cs = self.get_piece(t), t
            self.pieces[them][cap] = clear_bit(self.pieces[them][cap], cs); self.colors[them] = clear_bit(self.colors[them], cs); self.key ^= ZOBRIST_PIECES[them][cap][cs]
        self.stack[-1] = (self.stack[-1][0], self.stack[-1][1], self.stack[-1][2], self.stack[-1][3], cap)
        np = [KNIGHT, BISHOP, ROOK, QUEEN][fl & 0x3] if fl & PROMOTION_FLAG_MASK else p
        self.pieces[us][np] = set_bit(self.pieces[us][np], t); self.colors[us] = set_bit(self.colors[us], t); self.key ^= ZOBRIST_PIECES[us][np][t]
        if fl in (2, 3):
            rf, rt = ((H1, F1) if us == WHITE else (H8, F8)) if fl == 2 else ((A1, D1) if us == WHITE else (A8, D8))
            self.pieces[us][ROOK] = clear_bit(self.pieces[us][ROOK], rf); self.pieces[us][ROOK] = set_bit(self.pieces[us][ROOK], rt)
            self.colors[us] = clear_bit(self.colors[us], rf); self.colors[us] = set_bit(self.colors[us], rt)
        self.ep = f + 8 if (fl == FLAG_DOUBLE_PUSH and us == WHITE) else (f - 8 if (fl == FLAG_DOUBLE_PUSH and us == BLACK) else -1)
        if self.ep != -1: self.key ^= ZOBRIST_EP[self.ep % 8]
        if p == KING: self.castle &= (0xC if us == WHITE else 0x3)
        if f == A1 or t == A1: self.castle &= ~2
        if f == H1 or t == H1: self.castle &= ~1
        if f == A8 or t == A8: self.castle &= ~8
        if f == H8 or t == H8: self.castle &= ~4
        self.key ^= ZOBRIST_CASTLE[self.castle]; self.halfmove = 0 if (p == PAWN or cap != -1) else self.halfmove + 1
        if us == BLACK: self.fullmove += 1
        self.side, self.all_pieces = them, self.colors[0] | self.colors[1]; self.key ^= ZOBRIST_SIDE
    def unmake_move(self, m):
        f, t, fl = move_from(m), move_to(m), move_flag(m); self.key, self.castle, self.ep, self.halfmove, cap = self.stack.pop(); them, us = self.side, 1-self.side; self.side = us
        if us == BLACK: self.fullmove -= 1
        p = self.get_piece(t)
        if fl & PROMOTION_FLAG_MASK: self.pieces[us][p] = clear_bit(self.pieces[us][p], t); self.colors[us] = clear_bit(self.colors[us], t); p = PAWN
        else: self.pieces[us][p] = clear_bit(self.pieces[us][p], t); self.colors[us] = clear_bit(self.colors[us], t)
        self.pieces[us][p] = set_bit(self.pieces[us][p], f); self.colors[us] = set_bit(self.colors[us], f)
        if cap != -1:
            cs = (t - 8 if us == WHITE else t + 8) if fl == FLAG_EP_CAPTURE else t
            self.pieces[them][cap] = set_bit(self.pieces[them][cap], cs); self.colors[them] = set_bit(self.colors[them], cs)
        if fl in (2, 3):
            rf, rt = ((H1, F1) if us == WHITE else (H8, F8)) if fl == 2 else ((A1, D1) if us == WHITE else (A8, D8))
            self.pieces[us][ROOK] = clear_bit(self.pieces[us][ROOK], rt); self.pieces[us][ROOK] = set_bit(self.pieces[us][ROOK], rf)
            self.colors[us] = clear_bit(self.colors[us], rt); self.colors[us] = set_bit(self.colors[us], rf)
        self.all_pieces = self.colors[0] | self.colors[1]
    def to_fen(self):
        res = []
        for r in range(7, -1, -1):
            e, rank = 0, ""
            for f in range(8):
                sq = r * 8 + f; p = self.get_piece(sq)
                if p == -1: e += 1
                else: 
                    if e: rank += str(e); e = 0
                    char = PIECE_CHARS[p]; rank += char if get_bit(self.colors[WHITE], sq) else char.lower()
            if e: rank += str(e)
            res.append(rank)
        c = (('K' if self.castle&1 else '') + ('Q' if self.castle&2 else '') + ('k' if self.castle&4 else '') + ('q' if self.castle&8 else ''))
        return f"{'/'.join(res)} {'w' if self.side == WHITE else 'b'} {c if c else '-'} {SQUARE_NAMES[self.ep] if self.ep != -1 else '-'} {self.halfmove} {self.fullmove}"

def is_atk(b, sq, side):
    if sq == -1: return False
    if KNIGHT_ATTACKS[sq] & b.pieces[side][KNIGHT] or KING_ATTACKS[sq] & b.pieces[side][KING]: return True
    if PAWN_ATTACKS[1-side][sq] & b.pieces[side][PAWN]: return True
    blk = b.all_pieces
    return bool(get_bishop_atk(sq, blk) & (b.pieces[side][BISHOP] | b.pieces[side][QUEEN])) or bool(get_rook_atk(sq, blk) & (b.pieces[side][ROOK] | b.pieces[side][QUEEN]))

def gen_moves(b):
    moves, us, them = [], b.side, 1-b.side; occ, empty, pawns = b.all_pieces, ~b.all_pieces & UNIVERSE, b.pieces[us][PAWN]
    if us == WHITE:
        for t in iter_bits((pawns << 8) & empty):
            f = t - 8; [moves.append(encode_move(f,t,fl)) for fl in [8,9,10,11]] if t >= 56 else moves.append(encode_move(f,t,0))
        for t in iter_bits((((pawns & RANK_2) << 8) & empty) << 8 & empty): moves.append(encode_move(t-16,t,1))
        for t in iter_bits((pawns << 7) & ~FILE_H & b.colors[them]):
            f = t-7; [moves.append(encode_move(f,t,fl)) for fl in [12,13,14,15]] if t >= 56 else moves.append(encode_move(f,t,4))
        for t in iter_bits((pawns << 9) & ~FILE_A & b.colors[them]):
            f = t-9; [moves.append(encode_move(f,t,fl)) for fl in [12,13,14,15]] if t >= 56 else moves.append(encode_move(f,t,4))
        if b.ep != -1:
            if b.ep%8!=0 and get_bit(pawns,b.ep-9): moves.append(encode_move(b.ep-9,b.ep,5))
            if b.ep%8!=7 and get_bit(pawns,b.ep-7): moves.append(encode_move(b.ep-7,b.ep,5))
    else:
        for t in iter_bits((pawns >> 8) & empty):
            f = t + 8; [moves.append(encode_move(f,t,fl)) for fl in [8,9,10,11]] if t <= 7 else moves.append(encode_move(f,t,0))
        for t in iter_bits((((pawns & RANK_7) >> 8) & empty) >> 8 & empty): moves.append(encode_move(t+16,t,1))
        for t in iter_bits((pawns >> 9) & ~FILE_H & b.colors[them]):
            f = t+9; [moves.append(encode_move(f,t,fl)) for fl in [12,13,14,15]] if t <= 7 else moves.append(encode_move(f,t,4))
        for t in iter_bits((pawns >> 7) & ~FILE_A & b.colors[them]):
            f = t+7; [moves.append(encode_move(f,t,fl)) for fl in [12,13,14,15]] if t <= 7 else moves.append(encode_move(f,t,4))
        if b.ep != -1:
            if b.ep%8!=7 and get_bit(pawns,b.ep+9): moves.append(encode_move(b.ep+9,b.ep,5))
            if b.ep%8!=0 and get_bit(pawns,b.ep+7): moves.append(encode_move(b.ep+7,b.ep,5))
    for pt, fn in [(1, lambda s,o: KNIGHT_ATTACKS[s]), (2, get_bishop_atk), (3, get_rook_atk), (4, get_queen_atk), (5, lambda s,o: KING_ATTACKS[s])]:
        for f in iter_bits(b.pieces[us][pt]):
            atks = fn(f, occ) & ~b.colors[us]
            for t in iter_bits(atks): moves.append(encode_move(f, t, 4 if get_bit(b.colors[them], t) else 0))
    if us == WHITE:
        if (b.castle&1) and not (occ&0x60) and not is_atk(b,E1,them) and not is_atk(b,F1,them) and not is_atk(b,G1,them): moves.append(encode_move(E1,G1,2))
        if (b.castle&2) and not (occ&0xE) and not is_atk(b,E1,them) and not is_atk(b,D1,them) and not is_atk(b,C1,them): moves.append(encode_move(E1,C1,3))
    else:
        if (b.castle&4) and not (occ&0x6000000000000000) and not is_atk(b,E8,them) and not is_atk(b,F8,them) and not is_atk(b,G8,them): moves.append(encode_move(E8,G8,2))
        if (b.castle&8) and not (occ&0x0E00000000000000) and not is_atk(b,E8,them) and not is_atk(b,D8,them) and not is_atk(b,C8,them): moves.append(encode_move(E8,C8,3))
    legal = []
    for m in moves:
        b.make_move(m); ks = lsb(b.pieces[us][KING]) if b.pieces[us][KING] else -1
        if ks != -1 and not is_atk(b, ks, them): legal.append(m)
        b.unmake_move(m)
    return legal

PV = [100, 320, 330, 500, 900, 20000]
PST = [ [0]*64, [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,5,5,0,-20,-40,-30,5,10,15,15,10,5,-30,-30,0,15,20,20,15,0,-30,-30,5,15,20,20,15,5,-30,-30,0,10,15,15,10,0,-30,-40,-20,0,0,0,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50], [-20,-10,-10,-10,-10,-10,-10,-20,-10,5,0,0,0,0,5,-10,-10,10,10,10,10,10,10,-10,-10,0,10,10,10,10,0,-10,-10,5,5,10,10,5,5,-10,-10,0,5,10,10,5,0,-10,-10,0,0,0,0,0,0,-10,-20,-10,-10,-10,-10,-10,-10,-20], [0,0,0,5,5,0,0,0,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,5,10,10,10,10,10,10,5,0,0,0,0,0,0,0,0], [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,5,0,0,0,0,-10,-10,5,5,5,5,5,0,-10,0,0,5,5,5,5,0,-5,-5,0,5,5,5,5,0,-5,-10,0,5,5,5,5,0,-10,-10,0,0,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20], [20,30,10,0,0,10,30,20,20,20,0,0,0,0,20,20,-10,-20,-20,-20,-20,-20,-20,-10,-20,-30,-30,-40,-40,-30,-30,-20,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30] ]

def is_endgame(b):
    total = 0
    for c in range(2):
        for pt in [4, 3, 2, 1]: total += popcount(b.pieces[c][pt])
    return total <= 4

def eval_board(b):
    sc = [0, 0]
    for c in range(2):
        for pt in range(6):
            for sq in iter_bits(b.pieces[c][pt]): sc[c] += PV[pt] + PST[pt][sq ^ 56 if c == BLACK else sq]
    res = sc[WHITE] - sc[BLACK]
    # Check Bonus (increased from 20/20 to 50/50)
    wk, bk = (lsb(b.pieces[0][5]) if b.pieces[0][5] else -1), (lsb(b.pieces[1][5]) if b.pieces[1][5] else -1)
    if bk != -1 and is_atk(b, bk, 0): res += 50
    if wk != -1 and is_atk(b, wk, 1): res -= 50
    # Mobility Bonus (new)
    if wk != -1: res += len([1 for t in iter_bits(KING_ATTACKS[wk]) if not (b.colors[WHITE] & (1 << t))]) * 3
    if bk != -1: res -= len([1 for t in iter_bits(KING_ATTACKS[bk]) if not (b.colors[BLACK] & (1 << t))]) * 3
    # Pawn Structure (penalize doubled pawns on same file)
    for file in range(8):
        wh_pawns = b.pieces[WHITE][PAWN] & FILE_MASKS[file]
        if popcount(wh_pawns) > 1: res -= 10
    for file in range(8):
        bk_pawns = b.pieces[BLACK][PAWN] & FILE_MASKS[file]
        if popcount(bk_pawns) > 1: res += 10
    # Endgame Finisher
    if is_endgame(b):
        if wk != -1: res += (7-abs((wk%8)-3.5))*5 + (7-abs((wk//8)-3.5))*5
        if bk != -1:
            res -= (7-abs((bk%8)-3.5))*5 + (7-abs((bk//8)-3.5))*5
            res += (3-min(bk%8,7-(bk%8)))*10 + (3-min(bk//8,7-(bk//8)))*10
    return res if b.side == WHITE else -res

class Searcher:
    def __init__(self, b): self.b, self.tt, self.history, self.nodes, self.start, self.limit = b, {}, [[[0]*64 for _ in range(64)] for _ in range(2)], 0, 0, 3.5; self.killers = [[0, 0] for _ in range(100)]
    def qsearch(self, a, b):
        self.nodes += 1
        if self.nodes&2047==0 and time.time()-self.start > self.limit: raise Exception()
        sp = eval_board(self.b)
        if sp >= b: return b
        if a < sp: a = sp
        moves = sorted([m for m in gen_moves(self.b) if (move_flag(m)&4)], key=lambda x: 10*PV[self.b.get_piece(move_to(x)) if self.b.get_piece(move_to(x))!=-1 else 0], reverse=True)
        for m in moves[:15]:
            self.b.make_move(m); score = -self.qsearch(-b, -a); self.b.unmake_move(m)
            if score >= b: return b
            if score > a: a = score
        return a
    def negamax(self, d, ply, a, b):
        self.nodes += 1
        if self.nodes&2047==0 and time.time()-self.start > self.limit: raise Exception()
        e, tm = self.tt.get(self.b.key), 0
        if e:
            tm = e[3]
            if e[0]>=d:
                if e[2]==0: return e[1]
                if e[2]==1 and e[1]<=a: return a
                if e[2]==2 and e[1]>=b: return b
        if d==0: return self.qsearch(a, b)
        moves = gen_moves(self.b)
        if not moves: ks = lsb(self.b.pieces[self.b.side][KING]) if self.b.pieces[self.b.side][KING] else -1; return -100000+ply if (ks!=-1 and is_atk(self.b,ks,1-self.b.side)) else 0
        def score_move(m):
            if m==tm: return 2000000
            if m==self.killers[ply][0]: return 1500000
            if m==self.killers[ply][1]: return 1400000
            if move_flag(m)&4:
                v, at = (self.b.get_piece(move_to(m)) or 0), (self.b.get_piece(move_from(m)) or 0)
                return 1000000+10*PV[v]-PV[at]
            score = self.history[self.b.side][move_from(m)][move_to(m)]
            if ply < 2: score += 5000
            return score
        moves.sort(key=score_move, reverse=True)
        bs, bm, ao = -200000, 0, a
        for m in moves:
            self.b.make_move(m); score = -self.negamax(d-1, ply+1, -b, -a); self.b.unmake_move(m)
            if score > bs: bs, bm = score, m
            if score > a: a = score
            if a >= b:
                if not (move_flag(m)&4):
                    self.history[self.b.side][move_from(m)][move_to(m)] += d*d
                    if m != self.killers[ply][0]: self.killers[ply][1], self.killers[ply][0] = self.killers[ply][0], m
                break
        self.tt[self.b.key] = (d, bs, (0 if bs>ao and bs<b else (1 if bs<=ao else 2)), bm); return bs
    def search(self, t):
        self.start, self.limit, self.nodes, best = time.time(), t, 0, None
        try:
            for d in range(1, 100): 
                self.negamax(d, 0, -200000, 200000)
                if self.b.key in self.tt: best = self.tt[self.b.key][3]
                if time.time()-self.start > t*0.7: break
        except: pass
        if best is None or best == 0: l = gen_moves(self.b); return l[0] if l else 0
        return best

BOOK = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": "e2e4",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "c7c5",
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": "f1c4",
    "rnbqkbnr/pppp1ppp/8/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3": "g7g6",
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": "g8f6",
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": "b8c6",
}

def get_best_move(fen, t=3.5):
    try:
        parts = fen.split()
        if len(parts) < 4:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        core = " ".join(fen.split()[:4])
        for bf, move in BOOK.items():
            if " ".join(bf.split()[:4]) == core: return move
        b = Board(); b.load_fen(fen); moves = gen_moves(b)
        if not moves: return "0000"
        s = Searcher(b); m = s.search(t)
        if m == 0 or move_to_uci(m) == "0000": return move_to_uci(moves[0])
        return move_to_uci(m)
    except:
        try: b = Board(); b.load_fen(fen); l = gen_moves(b); return move_to_uci(l[0]) if l else "0000"
        except: return "0000"

def next_move(fen):
    return get_best_move(fen)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fen", type=str); parser.add_argument("--uci", action="store_true")
    args = parser.parse_args()
    if args.fen: print(get_best_move(args.fen))
    elif args.uci:
        print("id name FinalBot\nid author AI\nuciok")
        b = Board(); b.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        while True:
            try:
                line = input().split()
                if not line: continue
                if line[0]=="isready": print("readyok")
                elif line[0]=="position": b.load_fen(" ".join(line[2:8]) if len(line)>2 and line[1]=="fen" else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                elif line[0]=="go": print(f"bestmove {get_best_move(b.to_fen())}")
                elif line[0]=="quit": break
            except EOFError: break
            except: continue
    else:
        f = sys.stdin.read().strip(); print(get_best_move(f) if f else "0000")