import chess
import time
import random
import math

GLOBAL_HISTORY = set()

INF = 10_000_000
MATE_SCORE = 99000
CONTEMPT = -10

_LMR = [[0]*64 for _ in range(64)]
for _d in range(1, 64):
    for _m in range(1, 64):
        _LMR[_d][_m] = max(0, int(0.75 + math.log(_d) * math.log(_m) / 2.25))

SEE_VAL = {chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:20000}
MG_VAL  = {chess.PAWN:82, chess.KNIGHT:337,chess.BISHOP:365,chess.ROOK:477,chess.QUEEN:1025,chess.KING:0}
EG_VAL  = {chess.PAWN:94, chess.KNIGHT:281,chess.BISHOP:297,chess.ROOK:512,chess.QUEEN:936, chess.KING:0}

MG_PAWN  =[0,0,0,0,0,0,0,0,98,134,61,95,68,126,34,-11,-6,7,26,31,65,56,25,-20,-14,13,6,21,23,12,17,-23,-27,-2,-5,12,17,6,10,-25,-26,-4,-4,-10,3,3,33,-12,-35,-1,-20,-23,-15,24,38,-22,0,0,0,0,0,0,0,0]
EG_PAWN  =[0,0,0,0,0,0,0,0,178,173,158,134,147,132,165,187,94,100,85,67,56,53,82,84,32,24,13,5,-2,4,17,17,13,9,-3,-7,-7,-8,3,-1,4,7,-6,1,0,-5,-1,-8,13,8,8,10,13,0,2,-7,0,0,0,0,0,0,0,0]
MG_KNIGHT=[-167,-89,-34,-49,61,-97,-15,-107,-73,-41,72,36,23,62,7,-17,-47,60,37,65,84,129,73,44,-9,17,19,53,37,69,18,22,-13,4,16,13,28,19,21,-8,-23,-9,12,10,19,17,25,-16,-29,-53,-12,-3,-1,18,-14,-19,-105,-21,-58,-33,-17,-28,-19,-23]
EG_KNIGHT=[-58,-38,-13,-28,-31,-27,-63,-99,-25,-8,-25,-2,-9,-25,-24,-52,-24,-20,10,9,-1,-9,-19,-41,-17,3,22,22,22,11,8,-18,-18,-6,16,25,16,17,4,-18,-23,-3,-1,15,10,-3,-20,-22,-42,-20,-10,-5,-2,-20,-23,-44,-29,-51,-23,-15,-22,-18,-50,-64]
MG_BISHOP=[-29,4,-82,-37,-25,-42,7,-8,-26,16,-18,-13,30,59,18,-47,-16,37,43,40,35,50,37,-2,-4,5,19,50,37,37,7,-2,-6,13,13,26,34,12,10,4,0,15,15,15,14,27,18,10,4,15,16,0,7,21,33,1,-33,-3,-14,-21,-13,-12,-39,-21]
EG_BISHOP=[-14,-21,-11,-8,-7,-9,-17,-24,-8,-4,7,-12,-3,-13,-4,-14,2,-8,0,-1,-2,6,0,4,-3,9,12,9,14,10,3,2,-6,3,13,19,7,10,-3,-9,-12,-3,8,10,13,3,-7,-15,-14,-18,-7,-1,4,-9,-15,-27,-23,-9,-23,-5,-9,-16,-5,-17]
MG_ROOK  =[32,42,32,51,63,9,31,43,27,32,58,62,80,67,26,44,-5,19,26,36,17,45,61,16,-24,-11,7,26,24,35,-8,-20,-36,-26,-12,-1,9,-7,6,-23,-45,-25,-16,-17,3,0,-5,-33,-44,-16,-20,-9,-1,11,-6,-71,-19,-13,1,17,16,7,-37,-26]
EG_ROOK  =[13,10,18,15,12,-5,-7,6,11,13,13,11,-3,3,8,3,7,7,7,5,4,-3,-5,-3,4,3,13,1,2,1,-1,2,3,5,8,4,-5,-6,-8,-11,-4,0,-5,-1,-7,-12,-8,-16,-6,-6,0,2,-9,-9,-11,-3,-9,2,3,-1,-5,-13,4,-20]
MG_QUEEN =[-28,0,29,12,59,44,43,45,-24,-39,-5,1,-16,57,28,54,-13,-17,7,8,29,56,47,57,-27,-27,-16,-16,-1,17,-2,1,-9,-26,-9,-10,-2,-4,3,-3,-14,2,-11,-2,-5,2,14,5,-35,-8,11,2,8,15,-3,1,-1,-18,-9,10,-15,-25,-31,-50]
EG_QUEEN =[-9,22,22,27,27,19,10,20,-17,20,32,41,58,25,30,0,-20,6,9,49,47,35,19,9,3,22,24,45,57,40,57,36,-18,28,19,47,31,34,39,23,-16,-27,15,6,9,17,10,5,-22,-23,-30,-16,-16,-23,-36,-32,-33,-28,-22,-43,-5,-32,-20,-41]
MG_KING  =[-65,23,16,-15,-56,-34,2,13,29,-1,-20,-7,-8,-4,-38,-29,-9,24,2,-16,-20,6,22,-22,-17,-20,-12,-27,-30,-25,-14,-36,-49,-1,-27,-39,-46,-44,-33,-51,-14,-14,-22,-46,-44,-30,-15,-27,1,7,-8,-64,-43,-16,9,8,-15,36,12,-54,8,-28,24,14]
EG_KING  =[-74,-35,-18,-18,-11,15,4,-17,-12,17,14,17,17,38,23,11,10,17,23,15,20,45,44,13,-8,22,24,27,26,33,26,3,-18,-4,21,24,27,23,9,-11,-19,-3,11,21,23,16,7,-9,-27,-11,4,13,14,4,-5,-17,-53,-34,-21,-11,-28,-14,-24,-43]

MG_T={chess.PAWN:MG_PAWN,chess.KNIGHT:MG_KNIGHT,chess.BISHOP:MG_BISHOP,chess.ROOK:MG_ROOK,chess.QUEEN:MG_QUEEN,chess.KING:MG_KING}
EG_T={chess.PAWN:EG_PAWN,chess.KNIGHT:EG_KNIGHT,chess.BISHOP:EG_BISHOP,chess.ROOK:EG_ROOK,chess.QUEEN:EG_QUEEN,chess.KING:EG_KING}
PHASE_W={chess.PAWN:0,chess.KNIGHT:1,chess.BISHOP:1,chess.ROOK:2,chess.QUEEN:4,chess.KING:0}
MAX_PHASE=24

MG_PASS = [0, 5, 10, 20, 50, 90, 150, 0]
EG_PASS = [0, 30, 70, 140, 250, 450, 700, 0]

def _idx(sq,color):
    return (7-chess.square_rank(sq))*8+chess.square_file(sq) if color==chess.WHITE \
           else chess.square_rank(sq)*8+chess.square_file(sq)

def evaluate(board):
    if board.is_checkmate():
        return -MATE_SCORE if board.turn==chess.WHITE else MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    mg=[0,0]; eg=[0,0]; phase=0; wmat=bmat=0
    w_pc=[0]*8; b_pc=[0]*8
    w_pr=[[] for _ in range(8)]; b_pr=[[] for _ in range(8)]
    
    wk=board.king(chess.WHITE)
    bk=board.king(chess.BLACK)
    
    for sq,p in board.piece_map().items():
        c=0 if p.color==chess.WHITE else 1
        i=_idx(sq,p.color)
        pt=p.piece_type
        mg[c]+=MG_VAL[pt]+MG_T[pt][i]
        eg[c]+=EG_VAL[pt]+EG_T[pt][i]
        phase+=PHASE_W[pt]
        if pt!=chess.KING:
            if p.color==chess.WHITE: wmat+=MG_VAL[pt]
            else: bmat+=MG_VAL[pt]
            
            w = 0
            if pt in (chess.KNIGHT, chess.BISHOP): w = 15
            elif pt == chess.ROOK: w = 20
            elif pt == chess.QUEEN: w = 35
            elif pt == chess.PAWN: w = 5
            
            if w > 0:
                if c == 0 and bk is not None: mg[0] += (7 - chess.square_distance(sq, bk)) * w
                elif c == 1 and wk is not None: mg[1] += (7 - chess.square_distance(sq, wk)) * w
                
        if pt==chess.PAWN:
            f=chess.square_file(sq); r=chess.square_rank(sq)
            if c==0: w_pc[f]+=1; w_pr[f].append(r)
            else: b_pc[f]+=1; b_pr[f].append(r)
        if pt in (chess.KNIGHT, chess.BISHOP, chess.ROOK):
            mob = len(board.attacks(sq)) * 2
            if c==0: mg[0]+=mob; eg[0]+=mob
            else: mg[1]+=mob; eg[1]+=mob

    phase=min(phase,MAX_PHASE)
    score=((mg[0]-mg[1])*phase+(eg[0]-eg[1])*(MAX_PHASE-phase))//MAX_PHASE
    
    score += 14 * (1 if board.turn==chess.WHITE else -1)
    
    for f in range(8):
        if w_pc[f]>1: score-=12*(w_pc[f]-1)
        if b_pc[f]>1: score+=12*(b_pc[f]-1)
        if w_pc[f] and (f==0 or w_pc[f-1]==0) and (f==7 or w_pc[f+1]==0): score-=12
        if b_pc[f] and (f==0 or b_pc[f-1]==0) and (f==7 or b_pc[f+1]==0): score+=12
    
    for f in range(8):
        for r in w_pr[f]:
            passed=True
            for ff in range(max(0,f-1),min(8,f+2)):
                for br in b_pr[ff]:
                    if br>r: passed=False; break
                if not passed: break
            if passed:
                bonus=(MG_PASS[r]*phase+EG_PASS[r]*(MAX_PHASE-phase))//MAX_PHASE
                if phase<=12:
                    wk=board.king(chess.WHITE)
                    bk=board.king(chess.BLACK)
                    if wk is not None: bonus+=max(0,7-chess.square_distance(wk,chess.square(f,r)))*8
                    if bk is not None: bonus+=min(chess.square_distance(bk,chess.square(f,r))*8,48)
                score+=bonus
        for r in b_pr[f]:
            passed=True
            for ff in range(max(0,f-1),min(8,f+2)):
                for wr in w_pr[ff]:
                    if wr<r: passed=False; break
                if not passed: break
            if passed:
                rr=7-r
                bonus=(MG_PASS[rr]*phase+EG_PASS[rr]*(MAX_PHASE-phase))//MAX_PHASE
                if phase<=12:
                    bk=board.king(chess.BLACK)
                    wk=board.king(chess.WHITE)
                    if bk is not None: bonus+=max(0,7-chess.square_distance(bk,chess.square(f,r)))*8
                    if wk is not None: bonus+=min(chess.square_distance(wk,chess.square(f,r))*8,48)
                score-=bonus
    
    if len(board.pieces(chess.BISHOP,chess.WHITE))>=2: score+=35
    if len(board.pieces(chess.BISHOP,chess.BLACK))>=2: score-=35
    
    for sq in board.pieces(chess.ROOK,chess.WHITE):
        f=chess.square_file(sq)
        r=chess.square_rank(sq)
        if w_pc[f]==0:
            score+=20 if b_pc[f]==0 else 10
        if r==6: score+=40
    for sq in board.pieces(chess.ROOK,chess.BLACK):
        f=chess.square_file(sq)
        r=chess.square_rank(sq)
        if b_pc[f]==0:
            score-=20 if w_pc[f]==0 else 10
        if r==1: score-=40
    
    if phase>6:
        wk=board.king(chess.WHITE)
        if wk is not None:
            wkf,wkr=chess.square_file(wk),chess.square_rank(wk)
            shield=0
            for df in range(max(0,wkf-1),min(8,wkf+2)):
                for wr in w_pr[df]:
                    if wr in (wkr+1,wkr+2): shield+=1
            score+=shield*10
            if wkf in (3,4) and wkr<=1: score-=30
            if wkr>=2: score-=(wkr-1)*30
        bk=board.king(chess.BLACK)
        if bk is not None:
            bkf,bkr=chess.square_file(bk),chess.square_rank(bk)
            shield=0
            for df in range(max(0,bkf-1),min(8,bkf+2)):
                for br in b_pr[df]:
                    if br in (bkr-1,bkr-2): shield+=1
            score-=shield*10
            if bkf in (3,4) and bkr>=6: score+=30
            if bkr<=5: score+=(6-bkr)*30
    
    if wk is not None and bk is not None:
        score-=len(board.attackers(chess.BLACK,wk))*30
        score+=len(board.attackers(chess.WHITE,bk))*30
    
    adv=wmat-bmat
    
    if board.has_kingside_castling_rights(chess.WHITE): score+=15
    if board.has_queenside_castling_rights(chess.WHITE): score+=10
    if board.has_kingside_castling_rights(chess.BLACK): score-=15
    if board.has_queenside_castling_rights(chess.BLACK): score-=10
    
    if phase<=10 and wk is not None and bk is not None:
        wkr,wkf=chess.square_rank(wk),chess.square_file(wk)
        bkr,bkf=chess.square_rank(bk),chess.square_file(bk)
        wc=3-max(abs(wkr-3),abs(wkf-3))
        bc=3-max(abs(bkr-3),abs(bkf-3))
        score+=wc*25-bc*25
        kd=chess.square_distance(wk,bk)
        if adv>80: score+=(7-kd)*15
        elif adv<-80: score-=(7-kd)*15

    if abs(adv)>80 and wk is not None and bk is not None:
        kd=chess.square_distance(wk,bk)
        bkr,bkf=chess.square_rank(bk),chess.square_file(bk)
        wkr,wkf=chess.square_rank(wk),chess.square_file(wk)
        be=min(bkr,7-bkr,bkf,7-bkf)
        we=min(wkr,7-wkr,wkf,7-wkf)
        scale=min(abs(adv)//80,10)
        if adv>0: score+=((3-be)*100+(7-kd)*50)*scale//3
        else:     score-=((3-we)*100+(7-kd)*50)*scale//3

    if adv>50: score-=board.halfmove_clock*2
    elif adv<-50: score+=board.halfmove_clock*2
    
    if phase<=16 and abs(adv)>80:
        trade_bonus=(24-phase)*3
        if adv>0: score+=trade_bonus
        else: score-=trade_bonus
    
    moves_left=50-board.fullmove_number
    if moves_left<20 and abs(adv)>80:
        penalty=(20-moves_left)*40
        if adv>0: score-=penalty
        else: score+=penalty
        
    return score

def stm(board):
    s=evaluate(board)
    return s if board.turn==chess.WHITE else -s

_killers=[[None,None] for _ in range(64)]
_history={}
_counter={}

def score_move(board,move,ply,tt_move,prev_move=None):
    if move==tt_move: return 30000
    if board.is_capture(move):
        v=board.piece_type_at(move.to_square)
        if not v and board.is_en_passant(move): v=chess.PAWN
        a=board.piece_type_at(move.from_square)
        if v and a: return 23000+10*SEE_VAL[v]-SEE_VAL[a]
        return 23000
    if move.promotion: return 22000 if move.promotion==chess.QUEEN else 8000
    if ply<64:
        if move==_killers[ply][0]: return 12000
        if move==_killers[ply][1]: return 11000
    if prev_move and _counter.get((prev_move.from_square,prev_move.to_square))==move:
        return 10500
    return _history.get((move.from_square,move.to_square),0)

def ordered_moves(board,ply,tt_move=None,prev_move=None):
    moves=list(board.legal_moves)
    moves.sort(key=lambda m:score_move(board,m,ply,tt_move,prev_move),reverse=True)
    return moves

_tt={}
_timeout=False

def quiescence(board,alpha,beta,deadline,ply=0):
    global _timeout
    if time.time()>=deadline-0.01:
        _timeout=True
        return stm(board)
    
    in_check=board.is_check()
    if not in_check:
        sp=stm(board)
        if sp>=beta: return beta
        if sp>alpha: alpha=sp
    else:
        sp=-INF
    
    moves=list(board.legal_moves)
    if in_check and not moves:
        return -MATE_SCORE+ply
    
    moves.sort(key=lambda m:score_move(board,m,ply,None),reverse=True)
    
    for move in moves:
        is_cap=board.is_capture(move)
        is_promo=bool(move.promotion)
        if not in_check and not is_cap and not is_promo:
            continue
        if not in_check and is_cap and not is_promo:
            v=board.piece_type_at(move.to_square)
            if not v and board.is_en_passant(move): v=chess.PAWN
            if v and sp+SEE_VAL[v]+200<alpha: continue
        
        board.push(move)
        score=-quiescence(board,-beta,-alpha,deadline,ply+1)
        board.pop()
        if _timeout: return sp if not in_check else 0
        if score>=beta: return beta
        if score>alpha: alpha=score
    return alpha

def negamax(board,depth,alpha,beta,deadline,ply=0,null_ok=True,prev_move=None):
    global _timeout
    if time.time()>=deadline-0.01:
        _timeout=True
        return 0
    
    if ply>0:
        if board.is_repetition(2): return CONTEMPT
        if str(board._transposition_key()) in GLOBAL_HISTORY: return CONTEMPT
    
    in_check=board.is_check()
    if in_check: depth+=1
    
    is_pv=(beta-alpha)>1
    tt_move=None
    tk=board._transposition_key()
    te=_tt.get(tk)
    if te:
        td,ts,tf,tm=te
        tt_move=tm
        if td>=depth and not is_pv:
            if tf==0: return ts
            if tf==1: alpha=max(alpha,ts)
            if tf==2: beta=min(beta,ts)
            if alpha>=beta: return ts
    
    if depth<=0: return quiescence(board,alpha,beta,deadline,ply)
    
    se=stm(board)
    
    if not is_pv and not in_check and depth<=3:
        margin=200+150*depth
        if se-margin>=beta: return se-margin
    
    if null_ok and depth>=3 and not in_check and len(board.piece_map())>10 and not is_pv:
        R=3 if depth>=6 else 2
        board.push(chess.Move.null())
        ns=-negamax(board,depth-1-R,-beta,-beta+1,deadline,ply+1,False,None)
        board.pop()
        if _timeout: return 0
        if ns>=beta: return beta
    
    moves=ordered_moves(board,ply,tt_move,prev_move)
    if not moves:
        return (-MATE_SCORE+ply) if in_check else 0
    
    if len(moves)==1 and not in_check: depth+=1
    
    best=-INF; bmf=None; oa=alpha; searched=0; quiets=0
    fut_ok=not is_pv and not in_check and depth<=4
    fut_margin=[0,150,300,450,600]
    
    for move in moves:
        if _timeout: break
        is_cap=board.is_capture(move)
        is_promo=bool(move.promotion)
        gives_chk=board.gives_check(move) if (searched>=3 or fut_ok) and not is_cap and not is_promo else False
        tactical=is_cap or gives_chk or is_promo
        
        if fut_ok and searched>0 and not tactical:
            if depth<len(fut_margin) and se+fut_margin[depth]<=alpha:
                searched+=1; quiets+=1
                continue
        
        if not is_pv and depth<=3 and not in_check and not tactical:
            if quiets>=6+depth*3: continue
        
        board.push(move)
        
        if searched==0:
            score=-negamax(board,depth-1,-beta,-alpha,deadline,ply+1,True,move)
        else:
            reduction=0
            if searched>=3 and depth>=3 and not in_check and not tactical:
                reduction=_LMR[min(depth,63)][min(searched,63)]
                if is_pv: reduction=max(0,reduction-1)
                h=_history.get((move.from_square,move.to_square),0)
                if h<0: reduction+=1
                reduction=min(reduction,depth-2)
            
            score=-negamax(board,depth-1-reduction,-alpha-1,-alpha,deadline,ply+1,True,move)
            
            if reduction>0 and score>alpha and not _timeout:
                score=-negamax(board,depth-1,-alpha-1,-alpha,deadline,ply+1,True,move)
            
            if score>alpha and score<beta and not _timeout:
                score=-negamax(board,depth-1,-beta,-alpha,deadline,ply+1,True,move)
        
        board.pop()
        searched+=1
        if not tactical: quiets+=1
        
        if score>best: best=score; bmf=move
        alpha=max(alpha,score)
        if alpha>=beta:
            if not is_cap and ply<64:
                if _killers[ply][0]!=move:
                    _killers[ply][1]=_killers[ply][0]
                    _killers[ply][0]=move
            if prev_move and not is_cap:
                _counter[(prev_move.from_square,prev_move.to_square)]=move
            _history[(move.from_square,move.to_square)]=\
                _history.get((move.from_square,move.to_square),0)+depth*depth
            break
    
    if best>-INF:
        flag=0 if oa<best<beta else (1 if best>=beta else 2)
        old=_tt.get(tk)
        if old is None or depth>=old[0]:
            if len(_tt)>400000: _tt.clear()
            _tt[tk]=(depth,best,flag,bmf)
        
    return best



def best_move(board,time_limit=3.5):
    global _killers,_history,_counter,_timeout
    _killers=[[None,None] for _ in range(64)]
    _history={}
    _counter={}
    _timeout=False
    
    start=time.time()
    deadline=start+time_limit
    
    all_moves=list(board.legal_moves)
    
    for move in all_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move
        board.pop()
    
    random.shuffle(all_moves)
    all_moves.sort(key=lambda m:score_move(board,m,0,None),reverse=True)
    if not all_moves: return None
    if len(all_moves)==1: return all_moves[0]
    moves=all_moves
    
    best=moves[0]
    prev_score=0
    pieces=len(board.piece_map())
    max_d=20 if pieces<=6 else (16 if pieces<=10 else (14 if pieces<=16 else 12))
    
    for depth in range(1,max_d+1):
        elapsed=time.time()-start
        if elapsed>time_limit*0.6: break
        _timeout=False
        
        cb=None; cs=-INF; a=-INF
        
        for move in moves:
            if time.time()-start > time_limit*0.9:
                _timeout=True
                break
            
            board.push(move)
            if board.is_repetition(2):
                s=CONTEMPT
            else:
                s=-negamax(board,depth-1,-INF,-a,deadline,1,True,move)
            board.pop()
            
            if _timeout: break
            if s>cs: cs=s; cb=move
            if s>a: a=s
        
        if cb and not _timeout:
            best=cb
            prev_score=cs
            moves.remove(cb); moves.insert(0,cb)
        
        if _timeout: break
        if prev_score>=MATE_SCORE-100: break
    
    
    return best

def next_move(fen):
    global GLOBAL_HISTORY
    board=chess.Board(fen)
    
    if board.fullmove_number == 1 and board.turn == chess.WHITE:
        GLOBAL_HISTORY.clear()

    GLOBAL_HISTORY.add(str(board._transposition_key()))

    _tt.clear()
    move=best_move(board,time_limit=3.5)
    
    if move:
        board.push(move)
        GLOBAL_HISTORY.add(str(board._transposition_key()))
        board.pop()
        
    return str(move) if move else ""