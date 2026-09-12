import chess
import chess.polyglot
import time
import random

INF        = 1_000_000
MATE_SCORE = 900_000
DRAW_SCORE = 0
MAX_DEPTH  = 64
SEARCH_TIME = 3.4

PIECE_VALUES_MG = {
    chess.PAWN:   82,
    chess.KNIGHT: 337,
    chess.BISHOP: 365,
    chess.ROOK:   477,
    chess.QUEEN:  1025,
    chess.KING:   20000,
}
PIECE_VALUES_EG = {
    chess.PAWN:   94,
    chess.KNIGHT: 281,
    chess.BISHOP: 297,
    chess.ROOK:   512,
    chess.QUEEN:  936,
    chess.KING:   20000,
}

PHASE_WEIGHTS = {
    chess.PAWN:   0,
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK:   2,
    chess.QUEEN:  4,
    chess.KING:   0,
}
TOTAL_PHASE = 16*0 + 4*1 + 4*1 + 4*2 + 2*4

PAWN_MG = [
      0,  0,  0,  0,  0,  0,  0,  0,
     98,134, 61, 95, 68,126, 34,-11,
     -6,  7, 26, 31, 65, 56, 25,-20,
    -14, 13,  6, 21, 23, 12, 17,-23,
    -27, -2, -5, 12, 17,  6, 10,-25,
    -26, -4, -4,-10,  3,  3, 33,-12,
    -35, -1,-20,-23,-15, 24, 38,-22,
      0,  0,  0,  0,  0,  0,  0,  0,
]
PAWN_EG = [
      0,  0,  0,  0,  0,  0,  0,  0,
    178,173,158,134,147,132,165,187,
     94,100, 85, 67, 56, 53, 82, 84,
     32, 24, 13,  5, -2,  4, 17, 17,
     13,  9, -3, -7, -7, -8,  3, -1,
      4,  7, -6,  1,  0, -5, -1, -8,
     13,  8,  8, 10, 13,  0,  2, -7,
      0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_MG = [
    -167,-89,-34,-49, 61,-97,-15,-107,
     -73,-41, 72, 36, 23, 62,  7, -17,
     -47, 60, 37, 65, 84,129, 73,  44,
      -9, 17, 19, 53, 37, 69, 18,  22,
     -13,  4, 16, 13, 28, 19, 21,  -8,
     -23, -9, 12, 10, 19, 17, 25, -16,
     -29,-53,-12, -3, -1, 18,-14, -19,
    -105,-21,-58,-33,-17,-28,-19, -23,
]
KNIGHT_EG = [
    -58,-38,-13,-28,-31,-27,-63,-99,
    -25, -8,-25, -2, -9,-25,-24,-52,
    -24,-20, 10,  9, -1, -9,-19,-41,
    -17,  3, 22, 22, 22, 11,  8,-18,
    -18, -6, 16, 25, 16, 17,  4,-18,
    -23, -3, -1, 15, 10, -3,-20,-22,
    -42,-20,-10, -5, -2,-20,-23,-44,
    -29,-51,-23,-15,-22,-18,-50,-64,
]
BISHOP_MG = [
    -29,  4,-82,-37,-25,-42,  7, -8,
    -26, 16,-18,-13, 30, 59, 18,-47,
    -16, 37, 43, 40, 35, 50, 37, -2,
     -4,  5, 19, 50, 37, 37,  7, -2,
     -6, 13, 13, 26, 34, 12, 10,  4,
      0, 15, 15, 15, 14, 27, 18, 10,
      4, 15, 16,  0,  7, 21, 33,  1,
    -33, -3,-14,-21,-13,-12,-39,-21,
]
BISHOP_EG = [
    -14,-21,-11, -8, -7, -9,-17,-24,
     -8, -4,  7,-12, -3,-13, -4,-14,
      2, -8,  0, -1, -2,  6,  0,  4,
     -3,  9, 12,  9, 14, 10,  3,  2,
     -6,  3, 13, 19,  7, 10, -3, -9,
    -12, -3,  8, 10, 13,  3, -7,-15,
    -14,-18, -7, -1,  4, -9,-15,-27,
    -23, -9,-23, -5, -9,-16, -5,-17,
]
ROOK_MG = [
     32, 42, 32, 51, 63,  9, 31, 43,
     27, 32, 58, 62, 80, 67, 26, 44,
     -5, 19, 26, 36, 17, 45, 61, 16,
    -24,-11,  7, 26, 24, 35, -8,-20,
    -36,-26,-12, -1,  9, -7,  6,-23,
    -45,-25,-16,-17,  3,  0, -5,-33,
    -44,-16,-20, -9, -1, 11, -6,-71,
    -19,-13,  1, 17, 16,  7,-37,-26,
]
ROOK_EG = [
     13, 10, 18, 15, 12, 12,  8,  5,
     11, 13, 13, 11, -3,  3,  8,  3,
      7,  7,  7,  5,  4, -3, -5, -3,
      4,  3, 13,  1,  2,  1, -1,  2,
      3,  5,  8,  4, -5, -6, -8,-11,
     -4,  0, -5, -1, -7,-12, -8,-16,
     -6, -6,  0,  2, -9, -9,-11, -3,
     -9,  2,  3, -1, -5,-13,  4,-20,
]
QUEEN_MG = [
    -28,  0, 29, 12, 59, 44, 43, 45,
    -24,-39, -5,  1,-16, 57, 28, 54,
    -13,-17,  7,  8, 29, 56, 47, 57,
    -27,-27,-16,-16, -1, 17, -2,  1,
     -9,-26, -9,-10, -2, -4,  3, -3,
    -14,  2,-11, -2, -5,  2, 14,  5,
    -35, -8, 11,  2,  8, 15, -3,  1,
     -1,-18, -9, 10,-15,-25,-31,-50,
]
QUEEN_EG = [
     -9, 22, 22, 27, 27, 19, 10, 20,
    -17, 20, 32, 41, 58, 25, 30,  0,
    -20,  6,  9, 49, 47, 35, 19,  9,
      3, 22, 24, 45, 57, 40, 57, 36,
    -18, 28, 19, 47, 31, 34, 39, 23,
    -16,-27, 15,  6,  9, 17, 10,  5,
    -22,-23,-30,-16,-16,-23,-36,-32,
    -33,-28,-22,-43, -5,-32,-20,-41,
]
KING_MG = [
    -65, 23, 16,-15,-56,-34,  2, 13,
     29, -1,-20, -7, -8, -4,-38,-29,
     -9, 24,  2,-16,-20,  6, 22,-22,
    -17,-20,-12,-27,-30,-25,-14,-36,
    -49, -1,-27,-39,-46,-44,-33,-51,
    -14,-14,-22,-46,-44,-30,-15,-27,
      1,  7, -8,-64,-43,-16,  9,  8,
    -15, 36, 12,-54,  8,-28, 24, 14,
]
KING_EG = [
    -74,-35,-18,-18,-11, 15,  4,-17,
    -12, 17, 14, 17, 17, 38, 23, 11,
     10, 17, 23, 15, 20, 45, 44, 13,
     -8, 22, 24, 27, 26, 33, 26,  3,
    -18, -4, 21, 24, 27, 23,  9,-11,
    -19, -3, 11, 21, 23, 16,  7, -9,
    -27,-11,  4, 13, 14,  4,-5, -17,
    -53,-34,-21,-11,-28,-14,-24,-43,
]

PST = {
    chess.PAWN:   (PAWN_MG,   PAWN_EG),
    chess.KNIGHT: (KNIGHT_MG, KNIGHT_EG),
    chess.BISHOP: (BISHOP_MG, BISHOP_EG),
    chess.ROOK:   (ROOK_MG,   ROOK_EG),
    chess.QUEEN:  (QUEEN_MG,  QUEEN_EG),
    chess.KING:   (KING_MG,   KING_EG),
}

MIRROR = [56 ^ sq for sq in range(64)]

TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2

def evaluate(board: chess.Board) -> int:

    mg_white = 0
    eg_white = 0
    mg_black = 0
    eg_black = 0
    phase = 0

    piece_map = board.piece_map()
    for sq, piece in piece_map.items():
        pt = piece.piece_type
        pst_mg, pst_eg = PST[pt]
        if piece.color == chess.WHITE:
            idx = sq
            idx_w = MIRROR[sq]
            rank = chess.square_rank(sq)
            file = chess.square_file(sq)
            tbl_idx = (7 - rank) * 8 + file
            mg_white += PIECE_VALUES_MG[pt] + pst_mg[tbl_idx]
            eg_white += PIECE_VALUES_EG[pt] + pst_eg[tbl_idx]
        else:
            rank = chess.square_rank(sq)
            file = chess.square_file(sq)
            tbl_idx = rank * 8 + file
            mg_black += PIECE_VALUES_MG[pt] + pst_mg[tbl_idx]
            eg_black += PIECE_VALUES_EG[pt] + pst_eg[tbl_idx]

        phase += PHASE_WEIGHTS.get(pt, 0)

    if phase > TOTAL_PHASE:
        phase = TOTAL_PHASE

    mg_score = mg_white - mg_black
    eg_score = eg_white - eg_black

    score = (mg_score * phase + eg_score * (TOTAL_PHASE - phase)) // TOTAL_PHASE

    return score if board.turn == chess.WHITE else -score


_PT_ORDER = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
_PT_IDX   = {pt: i for i, pt in enumerate(_PT_ORDER)}

MVV_LVA = [[0]*7 for _ in range(7)]
for _v in _PT_ORDER:
    for _a in _PT_ORDER:
        MVV_LVA[_PT_IDX[_v]][_PT_IDX[_a]] = (
            PIECE_VALUES_MG[_v] * 10 - PIECE_VALUES_MG[_a]
        )


def mvv_lva_score(board: chess.Board, move: chess.Move) -> int:
    victim = board.piece_type_at(move.to_square)
    if victim is None:
        return 0
    attacker = board.piece_type_at(move.from_square)
    if attacker is None:
        return 0
    return MVV_LVA[_PT_IDX[victim]][_PT_IDX[attacker]]


class SearchState:
    def __init__(self):
        self.nodes      = 0
        self.killers    = [[None, None] for _ in range(MAX_DEPTH + 10)]
        self.history    = [[0] * 64 for _ in range(64)]  # [from][to]
        self.best_move  = None
        self.stop       = False
        self.deadline   = None  

    def store_killer(self, ply: int, move: chess.Move):
        if self.killers[ply][0] != move:
            self.killers[ply][1] = self.killers[ply][0]
            self.killers[ply][0] = move

    def is_killer(self, ply: int, move: chess.Move) -> bool:
        return move == self.killers[ply][0] or move == self.killers[ply][1]

def order_moves(board: chess.Board,
                moves,
                state: SearchState,
                ply: int,
                tt_move: chess.Move | None) -> list:
    scored = []
    for move in moves:
        if move == tt_move:
            score = 2_000_000
        elif move.promotion:
            score = 1_500_000 + PIECE_VALUES_MG.get(move.promotion, 0)
        elif board.is_capture(move):
            score = 1_000_000 + mvv_lva_score(board, move)
        elif state.is_killer(ply, move):
            score = 900_000
        else:
            score = state.history[move.from_square][move.to_square]
        scored.append((score, move))
    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored]

def quiescence(board: chess.Board,
               alpha: int,
               beta: int,
               state: SearchState) -> int:
    state.nodes += 1

    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    DELTA = PIECE_VALUES_MG[chess.QUEEN] + 200
    if stand_pat + DELTA < alpha:
        return alpha

    captures = list(board.generate_legal_captures())
    captures.sort(key=lambda m: -mvv_lva_score(board, m))

    for move in captures:
        board.push(move)
        score = -quiescence(board, -beta, -alpha, state)
        board.pop()

        if state.stop:
            return alpha

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


NULL_MOVE_REDUCTION = 3
#lol negamax
def negamax(board: chess.Board,
            depth: int,
            alpha: int,
            beta: int,
            ply: int,
            state: SearchState,
            tt: dict,
            pv_node: bool = True) -> int:

    state.nodes += 1

    if state.stop:
        return 0

    # 256 nodes is too much
    if state.deadline and (state.nodes & 127) == 0:
        if time.time() >= state.deadline:
            state.stop = True
            return 0

    if board.is_repetition(2) or board.is_fifty_moves():
        return DRAW_SCORE

    alpha = max(alpha, -(MATE_SCORE - ply))
    beta  = min(beta,   MATE_SCORE - ply)
    if alpha >= beta:
        return alpha

    in_check = board.is_check()

    if in_check:
        depth += 1

    if depth <= 0:
        return quiescence(board, alpha, beta, state)

    zh = chess.polyglot.zobrist_hash(board)
    tt_move = None
    tt_entry = tt.get(zh)
    if tt_entry is not None:
        tt_depth, tt_flag, tt_score, tt_mv_uci = tt_entry
        if tt_mv_uci:
            try:
                tt_move = chess.Move.from_uci(tt_mv_uci)
            except Exception:
                tt_move = None
        if tt_depth >= depth:
            if tt_flag == TT_EXACT:
                return tt_score
            elif tt_flag == TT_LOWER:
                alpha = max(alpha, tt_score)
            elif tt_flag == TT_UPPER:
                beta = min(beta, tt_score)
            if alpha >= beta:
                return tt_score

    if (not in_check
            and not pv_node
            and depth >= NULL_MOVE_REDUCTION + 1
            and board.fullmove_number > 1):
        has_pieces = bool(
            board.pieces(chess.KNIGHT, board.turn) |
            board.pieces(chess.BISHOP, board.turn) |
            board.pieces(chess.ROOK,   board.turn) |
            board.pieces(chess.QUEEN,  board.turn)
        )
        if has_pieces:
            board.push(chess.Move.null())
            null_score = -negamax(
                board,
                depth - NULL_MOVE_REDUCTION - 1,
                -beta, -beta + 1,
                ply + 1, state, tt, False
            )
            board.pop()
            if state.stop:
                return 0
            if null_score >= beta:
                return beta

    legal = list(board.legal_moves)
    if not legal:
        if in_check:
            return -(MATE_SCORE - ply)
        return DRAW_SCORE

    ordered = order_moves(board, legal, state, ply, tt_move)

    best_score = -INF
    best_move  = None
    orig_alpha = alpha
    moves_searched = 0

    for move in ordered:
        board.push(move)
        gives_check = board.is_check()

        if (moves_searched >= 4
                and depth >= 3
                and not in_check
                and not gives_check
                and not board.is_capture(move)
                and move.promotion is None):
            reduction = 1 + (moves_searched >= 10) + (depth >= 6)
            score = -negamax(board, depth - 1 - reduction, -alpha - 1, -alpha,
                             ply + 1, state, tt, False)
            if score > alpha:
                score = -negamax(board, depth - 1, -beta, -alpha,
                                 ply + 1, state, tt, False)
        elif moves_searched == 0:
            score = -negamax(board, depth - 1, -beta, -alpha,
                             ply + 1, state, tt, pv_node)
        else:
            score = -negamax(board, depth - 1, -alpha - 1, -alpha,
                             ply + 1, state, tt, False)
            if score > alpha and score < beta:
                score = -negamax(board, depth - 1, -beta, -alpha,
                                 ply + 1, state, tt, pv_node)

        board.pop()
        moves_searched += 1

        if state.stop:
            return best_score if best_move else 0

        if score > best_score:
            best_score = score
            best_move  = move

        if score > alpha:
            alpha = score
            if not board.is_capture(move):
                state.history[move.from_square][move.to_square] += depth * depth

        if alpha >= beta:
            if not board.is_capture(move):
                state.store_killer(ply, move)
            break

    if not state.stop and best_move is not None:
        if best_score <= orig_alpha:
            flag = TT_UPPER
        elif best_score >= beta:
            flag = TT_LOWER
        else:
            flag = TT_EXACT
        tt[zh] = (depth, flag, best_score, best_move.uci())

    return best_score

def root_search(board: chess.Board,
                depth: int,
                state: SearchState,
                tt: dict,
                last_score: int) -> tuple:

    legal = list(board.legal_moves)
    if not legal:
        return None, 0

    zh = chess.polyglot.zobrist_hash(board)
    tt_move = None
    entry = tt.get(zh)
    if entry and entry[3]:
        try:
            tt_move = chess.Move.from_uci(entry[3])
        except Exception:
            pass

    ordered = order_moves(board, legal, state, 0, tt_move)

    alpha = -INF
    beta  = INF
    best_move = ordered[0]
    best_score = -INF
    moves_searched = 0

    for move in ordered:
        if state.stop:
            return None, last_score

        board.push(move)
        gives_check = board.is_check()

        if moves_searched == 0:
            score = -negamax(board, depth - 1, -beta, -alpha, 1, state, tt, True)
        else:
            if (moves_searched >= 4
                    and depth >= 3
                    and not gives_check
                    and not board.is_capture(move)
                    and move.promotion is None):
                reduction = 1 + (moves_searched >= 10) + (depth >= 6)
                score = -negamax(board, depth - 1 - reduction, -alpha - 1, -alpha, 1, state, tt, False)
                if score > alpha and not state.stop:
                    score = -negamax(board, depth - 1, -beta, -alpha, 1, state, tt, True)
            else:
                score = -negamax(board, depth - 1, -alpha - 1, -alpha, 1, state, tt, False)
                if score > alpha and score < beta and not state.stop:
                    score = -negamax(board, depth - 1, -beta, -alpha, 1, state, tt, True)

        board.pop()

        if state.stop:
            return None, last_score

        if score > best_score:
            best_score = score
            best_move  = move

        if score > alpha:
            alpha = score

        moves_searched += 1

    tt[zh] = (depth, TT_EXACT, best_score, best_move.uci())
    return best_move.uci(), best_score

def next_move(fen: str) -> str:

    board    = chess.Board(fen)
    state    = SearchState()
    tt       = {}
    deadline = time.time() + SEARCH_TIME
    state.deadline = deadline

    legal = list(board.legal_moves)
    if not legal:
        return None
    best_uci   = legal[0].uci()
    last_score = 0

    for depth in range(1, MAX_DEPTH + 1):
        if time.time() >= deadline:
            break

        state.stop  = False
        state.nodes = 0

        uci, score = root_search(board, depth, state, tt, last_score)

        if state.stop or uci is None:
            break 

        best_uci   = uci
        last_score = score

        if score > MATE_SCORE - 100:
            break

    return best_uci
