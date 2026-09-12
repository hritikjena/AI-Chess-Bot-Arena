"""
TOTEM - The Chess Bot
Full-featured chess engine with ELO slider, time controls, assistance mode, game review, custom FEN starting positions, and tournament hooks.
100% Offline - No External APIs used.
"""
import chess
import pygame
import sys
import time
import random
import math

# ── Window / Board layout ──────────────────────────────────────────
WIN_W, WIN_H = 1100, 720
BOARD_PX     = 560
SQ           = BOARD_PX // 8
BX           = 20          # board left
BY           = 80          # board top
EVAL_X       = BX + BOARD_PX + 14
EVAL_W       = 16
PANEL_X      = EVAL_X + EVAL_W + 10
PANEL_W      = WIN_W - PANEL_X - 10
FPS          = 60

# ── Palette ──────────────────────────────────────────────
G_BG          = (28, 28, 28)
G_DARK_SQ     = (60, 60, 60)
G_LIGHT_SQ    = (95, 95, 95)
G_ACCENT      = (200, 40, 40)      # red
G_ACCENT2     = (40, 160, 220)     # blue
G_GREEN       = (80, 200, 80)
G_GOLD        = (220, 180, 40)
G_WHITE_PC    = (220, 220, 210)
G_BLACK_PC    = (180, 40, 40)
G_HIGHLIGHT   = (230, 200, 40, 140)
G_LAST_MOVE   = (200, 160, 30, 110)
G_CHECK       = (220, 40, 40, 160)
G_EVAL_W      = (230, 230, 220)
G_EVAL_B      = (35, 35, 35)
G_PANEL_BG    = (22, 22, 22)
G_BTN         = (50, 50, 50)
G_BTN_HOV     = (70, 70, 70)
BADGE_COLS = {
    "brilliant": (30, 190, 255),
    "great":     (120, 220, 80),
    "good":      (80, 190, 80),
    "best":      (220, 180, 40),
    "book":      (160, 120, 220),
    "inaccurate":(220, 160, 40),
    "mistake":   (220, 100, 40),
    "miss":      (200, 60, 60),
    "blunder":   (220, 40, 40),
}
BADGE_SYM = {
    "brilliant": "!!",  "great": "!",  "good": "✓",  "best": "★",
    "book": "📖",       "inaccurate": "?!", "mistake": "?", "miss": "✗", "blunder": "??",
}

ELO_MIN, ELO_MAX = 400, 3000
ELO_TIERS = [
    (400,  700,  "Beginner",     (160,160,160)),
    (700,  1000, "Novice",       (100,180,100)),
    (1000, 1300, "Intermediate", (80, 160,220)),
    (1300, 1600, "Advanced",     (160,100,220)),
    (1600, 1900, "Expert",       (220,160, 50)),
    (1900, 2200, "Master",       (220,100, 50)),
    (2200, 2500, "Grandmaster",  (220, 60, 60)),
    (2500, 3001, "Magnus Tier",  ( 30,190,255)),
]
TIME_OPTIONS = [("∞ None",0),("3 min",180),("5 min",300),("10 min",600),
                ("15 min",900),("20 min",1200),("30 min",1800)]
MODES = ["Assistance","Independent","Review After"]

def elo_tier(elo):
    for lo,hi,lbl,col in ELO_TIERS:
        if lo<=elo<hi: return lbl,col
    return "Magnus Tier",(30,190,255)

def elo_to_params(elo):
    t=(elo-ELO_MIN)/(ELO_MAX-ELO_MIN)
    depth=max(1,min(6,int(1+t*5)))
    error=max(0.0, 0.80-t*1.05)
    return depth, error

def elo_desc(elo):
    if elo<700:   return "Lots of blunders • Perfect for beginners"
    elif elo<1000: return "Avoids blunders • Casual opponent"
    elif elo<1300: return "Tactical awareness • Club-level"
    elif elo<1600: return "Solid positional play • Punishes mistakes"
    elif elo<1900: return "Strong tactics • Very challenging"
    elif elo<2200: return "Near-master strength • Deep calculation"
    elif elo<2500: return "Grandmaster strength • Ruthless"
    else:          return "Maximum strength • Good luck!"

# ── PST ──────────────────────────────────────────────────────────
PST={
    chess.PAWN:[
        0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,
        10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,
        0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,
        5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0],
    chess.KNIGHT:[
        -50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,
        -30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,
        -30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,
        -40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
    chess.BISHOP:[
        -20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,
        -10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,
        -10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,
        -10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
    chess.ROOK:[
        0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,
        -5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
        -5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
        -5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
    chess.QUEEN:[
        -20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,
        -10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,
        0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,
        -10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
    chess.KING:[
        -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,
        20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20],
}
PV={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,
    chess.ROOK:500,chess.QUEEN:900,chess.KING:20000}

# ── ENGINE ───────────────────────────────────────────────────────
class Engine:
    def __init__(self,elo=1200):
        self.elo=elo
        self.depth, self.error=elo_to_params(elo)
        self.best=None; self._rd=1; self.t0=0
        self.TL=3.5   # 3.5 sec to safely meet < 4.0 sec constraints for tournament

    def psq(self,pc,sq,col):
        tbl=PST.get(pc.piece_type,[0]*64)
        idx=((7-chess.square_rank(sq))*8+chess.square_file(sq)
             if col==chess.WHITE else chess.square_rank(sq)*8+chess.square_file(sq))
        return tbl[idx]

    def eval(self,board):
        if board.is_checkmate(): return -99999 if board.turn==chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition(): return 0
        s=0
        for sq in chess.SQUARES:
            p=board.piece_at(sq)
            if p: v=PV[p.piece_type]+self.psq(p,sq,p.color); s+=v if p.color==chess.WHITE else -v
        ts=board.turn
        board.turn=chess.WHITE; wm=board.legal_moves.count()
        board.turn=chess.BLACK; bm=board.legal_moves.count()
        board.turn=ts; s+=(wm-bm)*5
        if board.is_check(): s+=(-15 if board.turn==chess.WHITE else 15)
        return s

    def order(self,board,moves):
        def sc(m):
            s=0
            if board.is_capture(m):
                v=board.piece_at(m.to_square); a=board.piece_at(m.from_square)
                if v and a: s+=10*PV[v.piece_type]-PV[a.piece_type]
            if m.promotion: s+=PV[m.promotion]
            board.push(m)
            if board.is_check(): s+=50
            board.pop()
            return -s
        return sorted(moves,key=sc)

    def mm(self,board,d,a,b,mx):
        if time.time()-self.t0>=self.TL: return self.eval(board)
        if d==0 or board.is_game_over(claim_draw=True): return self.eval(board)
        moves=self.order(board,list(board.legal_moves))
        if mx:
            best=-1e9
            for m in moves:
                board.push(m); v=self.mm(board,d-1,a,b,False); board.pop()
                if v>best:
                    best=v
                    if d==self._rd: self.best=m
                a=max(a,best)
                if b<=a: break
            return best
        else:
            best=1e9
            for m in moves:
                board.push(m); v=self.mm(board,d-1,a,b,True); board.pop()
                best=min(best,v); b=min(b,best)
                if b<=a: break
            return best

    def move(self,board):
        self.t0=time.time(); self.best=None
        legal=list(board.legal_moves)
        if not legal: return None
        if random.random()<self.error: return random.choice(legal)
        d=self.depth+(1 if board.legal_moves.count()<10 and self.depth<6 else 0)
        for dep in range(1,d+1):
            if time.time()-self.t0>=self.TL: break
            self._rd=dep
            self.mm(board,dep,-1e9,1e9,board.turn==chess.WHITE)
        return self.best or random.choice(legal)

    def classify(self,board,move):
        before=self.eval(board)
        board.push(move); after=self.eval(board); board.pop()
        d=after-before if board.turn==chess.WHITE else before-after
        if d>=300: return "brilliant"
        elif d>=150: return "great"
        elif d>=50: return "good"
        elif d>=0: return "best"
        elif d>=-30: return "inaccurate"
        elif d>=-100: return "mistake"
        elif d>=-200: return "miss"
        else: return "blunder"

    def best_in_pos(self,board):
        saved_tl=self.TL; self.TL=1.0
        m=self.move(board); self.TL=saved_tl
        return m

# ────────────────────────────────────────
def next_move(fen):
    """
    Tournament Hook: Takes FEN, Returns UCI inside 4s limit.
    This fulfills ALL tournament requirements in your PDF.
    """
    board = chess.Board(fen)
    bot = Engine(elo=3000) # Max strength for tournament
    best_move_obj = bot.move(board)
    if best_move_obj:
        return best_move_obj.uci()
    return "0000"

# ── PIECE GLYPHS ─────────────────────────────────────────────────
GLYPHS={
    (chess.PAWN,chess.WHITE):"♙",(chess.KNIGHT,chess.WHITE):"♘",
    (chess.BISHOP,chess.WHITE):"♗",(chess.ROOK,chess.WHITE):"♖",
    (chess.QUEEN,chess.WHITE):"♕",(chess.KING,chess.WHITE):"♔",
    (chess.PAWN,chess.BLACK):"♟",(chess.KNIGHT,chess.BLACK):"♞",
    (chess.BISHOP,chess.BLACK):"♝",(chess.ROOK,chess.BLACK):"♜",
    (chess.QUEEN,chess.BLACK):"♛",(chess.KING,chess.BLACK):"♚",
}

def make_pieces(sz):
    try: f=pygame.font.SysFont("segoeuisymbol",int(sz*0.80))
    except: f=pygame.font.SysFont("dejavusans",int(sz*0.80))
    out={}
    for (pt,col),g in GLYPHS.items():
        sh=f.render(g,True,(0,0,0))
        pc_col=G_WHITE_PC if col==chess.WHITE else G_BLACK_PC
        mn=f.render(g,True,pc_col)
        s=pygame.Surface((sz,sz),pygame.SRCALPHA)
        ox=(sz-mn.get_width())//2; oy=(sz-mn.get_height())//2
        s.blit(sh,(ox+2,oy+2)); s.blit(mn,(ox,oy))
        out[(pt,col)]=s
    return out

# ── LOBBY ────────────────────────────────────────────────────────
class Lobby:
    SLX=60; SLY=310; SLW=320; SLH=8

    def __init__(self,fonts,pieces):
        self.fonts=fonts; self.pieces=pieces
        self.elo=1200; self.drag=False
        self.time_idx=0       
        self.mode_idx=1       
        self._a=0.0

    def _ex(self,e): return int(self.SLX+(e-ELO_MIN)/(ELO_MAX-ELO_MIN)*self.SLW)
    def _xe(self,x):
        t=max(0.,min(1.,(x-self.SLX)/self.SLW))
        return int(round((ELO_MIN+t*(ELO_MAX-ELO_MIN))/50)*50)

    def hit(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            mx,my=event.pos
            tx=self._ex(self.elo)
            if abs(mx-tx)<=16 and abs(my-self.SLY)<=16: self.drag=True
            elif self.SLX<=mx<=self.SLX+self.SLW and abs(my-self.SLY)<=12:
                self.elo=self._xe(mx)
            for i,(lbl,_) in enumerate(TIME_OPTIONS):
                bx=self.SLX+i*64; by=380; bw=60; bh=28
                row=i//4; col2=i%4
                bx2=self.SLX+col2*80; by2=390+row*38
                if bx2<=mx<=bx2+76 and by2<=my<=by2+30:
                    self.time_idx=i
            for i,m in enumerate(MODES):
                bx2=self.SLX+i*116; by2=510
                if bx2<=mx<=bx2+112 and by2<=my<=by2+34:
                    self.mode_idx=i
            
            # PLAY Button
            px2=WIN_W//2-120; py2=580; pw=240; ph=50
            if px2<=mx<=px2+pw and py2<=my<=py2+ph:
                return "play"
                
            # ADD FEN Button
            py_fen = 640; ph_fen = 40
            if px2<=mx<=px2+pw and py_fen<=my<=py_fen+ph_fen:
                return "fen"
                
        if event.type==pygame.MOUSEBUTTONUP: self.drag=False
        if event.type==pygame.MOUSEMOTION and self.drag:
            self.elo=self._xe(event.pos[0])
        return None

    def draw(self,surf,dt):
        self._a+=dt*0.5
        surf.fill(G_BG)
        for r in range(260,0,-50):
            a=max(0,int(4+3*math.sin(self._a+r*0.02)))
            gs=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(gs,(*G_ACCENT,a),(r,r),r)
            surf.blit(gs,(WIN_W//2-r,200-r))
            
        t_str = "T O T E M   -   T H E   C H E S S   B O T"
        t=self.fonts["big"].render(t_str,True,(0,188,212))
        ts=self.fonts["big"].render(t_str,True,(0,60,90))
        surf.blit(ts,(WIN_W//2-t.get_width()//2+2,20))
        surf.blit(t, (WIN_W//2-t.get_width()//2,   18))

        lx=self.SLX; cx=lx+170
        self.fonts["med"].render  
        surf.blit(self.fonts["med"].render("BOT STRENGTH",True,(180,180,180)),(lx,90))

        tl,tc=elo_tier(self.elo)
        bdg=pygame.Surface((180,30),pygame.SRCALPHA)
        pygame.draw.rect(bdg,(*tc,40),(0,0,180,30),border_radius=15)
        pygame.draw.rect(bdg,(*tc,200),(0,0,180,30),2,border_radius=15)
        surf.blit(bdg,(lx,116))
        bt=self.fonts["sm"].render(tl,True,tc)
        surf.blit(bt,(lx+90-bt.get_width()//2,122))

        en=self.fonts["elo"].render(str(self.elo),True,(240,240,240))
        surf.blit(en,(lx+90-en.get_width()//2,150))

        tn=(self.elo-ELO_MIN)/(ELO_MAX-ELO_MIN); fw=int(tn*self.SLW)
        pygame.draw.rect(surf,(50,50,50),(self.SLX,self.SLY-4,self.SLW,8),border_radius=4)
        if fw>0: pygame.draw.rect(surf,G_ACCENT,(self.SLX,self.SLY-4,fw,8),border_radius=4)
        for te in [400,700,1000,1300,1600,1900,2200,2500,3000]:
            tx2=self._ex(te)
            pygame.draw.line(surf,(80,80,80),(tx2,self.SLY-6),(tx2,self.SLY+6),1)
            lt=self.fonts["xs"].render(str(te),True,(70,70,70))
            surf.blit(lt,(tx2-lt.get_width()//2,self.SLY+8))
            
        thx=self._ex(self.elo); mpos=pygame.mouse.get_pos()
        hov=abs(mpos[0]-thx)<=16 and abs(mpos[1]-self.SLY)<=16
        gl=pygame.Surface((40,40),pygame.SRCALPHA)
        pygame.draw.circle(gl,(*G_ACCENT,60 if hov else 25),(20,20),20)
        surf.blit(gl,(thx-20,self.SLY-20))
        pygame.draw.circle(surf,(200,60,60) if self.drag else G_ACCENT,(thx,self.SLY),12)
        pygame.draw.circle(surf,(240,240,240),(thx,self.SLY),12,2)
        pygame.draw.circle(surf,(240,240,240),(thx,self.SLY),4)
        dc=self.fonts["xs"].render(elo_desc(self.elo),True,(120,120,120))
        surf.blit(dc,(lx,self.SLY+28))

        surf.blit(self.fonts["med"].render("TIME CONTROL",True,(180,180,180)),(lx,370))
        for i,(lbl,_) in enumerate(TIME_OPTIONS):
            row=i//4; col2=i%4
            bx2=lx+col2*80; by2=395+row*38; bw2=76; bh2=30
            sel=self.time_idx==i
            col3=G_ACCENT2 if sel else G_BTN
            pygame.draw.rect(surf,col3,(bx2,by2,bw2,bh2),border_radius=6)
            pygame.draw.rect(surf,(200,200,200) if sel else (60,60,60),(bx2,by2,bw2,bh2),1,border_radius=6)
            lt=self.fonts["xs"].render(lbl,True,(255,255,255) if sel else (160,160,160))
            surf.blit(lt,(bx2+bw2//2-lt.get_width()//2,by2+bh2//2-lt.get_height()//2))

        surf.blit(self.fonts["med"].render("PLAY MODE",True,(180,180,180)),(lx,476))
       
        mode_desc=["","",""]
        for i,m in enumerate(MODES):
            bx2=lx+i*116; by2=498; bw2=112; bh2=34
            sel=self.mode_idx==i
            col3=G_GREEN if sel else G_BTN
            pygame.draw.rect(surf,col3,(bx2,by2,bw2,bh2),border_radius=7)
            pygame.draw.rect(surf,(200,200,200) if sel else (60,60,60),(bx2,by2,bw2,bh2),1,border_radius=7)
            lt=self.fonts["sm"].render(m,True,(255,255,255))
            surf.blit(lt,(bx2+bw2//2-lt.get_width()//2,by2+8))
            if sel:
                dt2=self.fonts["xs"].render(mode_desc[i],True,(200,255,200))
                surf.blit(dt2,(bx2+bw2//2-dt2.get_width()//2,by2+22))

        rx=WIN_W//2+60; ry=90; rsq=34
        for sq in chess.SQUARES:
            f=chess.square_file(sq); r=chess.square_rank(sq)
            x=rx+f*rsq; y=ry+(7-r)*rsq
            c=G_LIGHT_SQ if (f+r)%2==0 else G_DARK_SQ
            pygame.draw.rect(surf,c,(x,y,rsq,rsq))
        b2=chess.Board()
        try: pf=pygame.font.SysFont("segoeuisymbol",26)
        except: pf=pygame.font.SysFont("dejavusans",26)
        for sq in chess.SQUARES:
            pc=b2.piece_at(sq)
            if pc:
                f=chess.square_file(sq); r=chess.square_rank(sq)
                x=rx+f*rsq; y=ry+(7-r)*rsq
                g=GLYPHS[(pc.piece_type,pc.color)]
                sh=pf.render(g,True,(0,0,0))
                mn=pf.render(g,True,G_WHITE_PC if pc.color==chess.WHITE else G_BLACK_PC)
                surf.blit(sh,(x+(rsq-mn.get_width())//2+1,y+(rsq-mn.get_height())//2+1))
                surf.blit(mn,(x+(rsq-mn.get_width())//2,y+(rsq-mn.get_height())//2))

        iy=ry+8*rsq+14
        info=[
            ("Assistance","Hint button suggests your best move in real time."),
            ("Independent","Play alone. Review available after the game."),
            ("Review After","Full annotated review with stats when game ends."),
        ]
        surf.blit(self.fonts["sm"].render(f"Mode: {MODES[self.mode_idx]}",True,G_GREEN),(rx,iy))
        desc2=info[self.mode_idx][1]
        dw=self.fonts["xs"].render(desc2,True,(140,140,140))
        surf.blit(dw,(rx,iy+18))

        # Main PLAY button
        px2=WIN_W//2-120; py2=580; pw=240; ph=50
        mpos2=pygame.mouse.get_pos()
        bh3=px2<=mpos2[0]<=px2+pw and py2<=mpos2[1]<=py2+ph
        pygame.draw.rect(surf,(180,50,50) if bh3 else G_ACCENT,(px2,py2,pw,ph),border_radius=25)
        pygame.draw.rect(surf,(255,180,180),(px2,py2,pw,ph),2,border_radius=25)
        pt3=self.fonts["btn"].render("▶  PLAY",True,(255,255,255))
        surf.blit(pt3,(px2+pw//2-pt3.get_width()//2,py2+ph//2-pt3.get_height()//2))

        # ADD FEN button
        py_fen=640; ph_fen=40
        bh_fen = px2<=mpos2[0]<=px2+pw and py_fen<=mpos2[1]<=py_fen+ph_fen
        pygame.draw.rect(surf,(80,80,80) if bh_fen else G_BTN,(px2,py_fen,pw,ph_fen),border_radius=20)
        pygame.draw.rect(surf,(150,150,150),(px2,py_fen,pw,ph_fen),1,border_radius=20)
        pt_fen=self.fonts["sm"].render("+ ADD FEN",True,(230,230,230))
        surf.blit(pt_fen,(px2+pw//2-pt_fen.get_width()//2,py_fen+ph_fen//2-pt_fen.get_height()//2))

# ── GAME STATE ────────────────────────────────────────────────────
class GS:
    def __init__(self,elo,time_sec,mode_idx, start_fen=None):
        if start_fen:
            self.board = chess.Board(start_fen)
            self.human = self.board.turn 
        else:
            self.board = chess.Board()
            self.human = random.choice([chess.WHITE,chess.BLACK])
            
        self.engine=Engine(elo); self.elo=elo
        self.mode=mode_idx   
        self.sel=None; self.targets=[]; self.last=None
        self.eval_s=0.0; self.eval_d=0.0
        self.thinking=False; self.think_t=0
        self.badge=""; self.badge_sq=None; self.badge_t=0
        self.over_msg=""
        # History format: (san, badge, color_that_moved, fen)
        self.log=[]          
        self.log.append(("Start" if not start_fen else "FEN Start","",None,self.board.fen())) 
        self.view_idx=0 
        
        self.promo=None
        self.use_timer=(time_sec>0)
        self.white_t=float(time_sec); self.black_t=float(time_sec)
        self.active_clock=None
        self.last_tick=time.time()
        self.hint_sq=None; self.hint_t=0
        self.review=None    

    def bot_col(self): return chess.BLACK if self.human==chess.WHITE else chess.WHITE
    def flipped(self): return self.human==chess.BLACK
    
    def is_viewing_history(self):
        return self.view_idx < len(self.log) - 1

    def sq_px(self,sq,flip=False):
        f=chess.square_file(sq); r=chess.square_rank(sq)
        if flip: f=7-f; r=7-r
        return BX+f*SQ, BY+(7-r)*SQ

    def px_sq(self,px,py,flip=False):
        f=(px-BX)//SQ; r=7-(py-BY)//SQ
        if flip: f=7-f; r=7-r
        return chess.square(f,r) if 0<=f<=7 and 0<=r<=7 else None

    def tick_clock(self):
        if not self.use_timer or self.over_msg or self.active_clock is None or self.thinking:
            self.last_tick = time.time()   
            return
        now = time.time()
        elapsed = now - self.last_tick
        self.last_tick = now
 
        if elapsed > 1.0: elapsed = 1.0   
        if self.active_clock == chess.WHITE:
            self.white_t = max(0.0, self.white_t - elapsed)
            if self.white_t <= 0:
                self.active_clock = None
                winner = "Black" if self.human == chess.BLACK else "Bot"
                self.over_msg = f"Time out!\n{winner} wins on time"
        else:
            self.black_t = max(0.0, self.black_t - elapsed)
            if self.black_t <= 0:
                self.active_clock = None
                winner = "White" if self.human == chess.WHITE else "Bot"
                self.over_msg = f"Time out!\n{winner} wins on time"

    def fmt_time(self,secs):
        if secs<=0: return "0:00"
        m=int(secs)//60; s=int(secs)%60
        return f"{m}:{s:02d}"

    def do_move(self,move,is_human):
        badge=self.engine.classify(self.board,move)
        san=self.board.san(move)
        col=self.board.turn
        self.board.push(move); self.last=move
        self.eval_s=self.engine.eval(self.board)
        self.badge=badge; self.badge_sq=move.to_square; self.badge_t=2.5
        self.log.append((san,badge,col,self.board.fen()))
        self.view_idx = len(self.log) - 1 # Snap to latest move
        self.hint_sq=None
        if self.use_timer:
            self.active_clock = self.board.turn   
            self.last_tick = time.time()           
        if self.board.is_game_over(claim_draw=True):
            self.active_clock = None
            self._set_over()

    def _set_over(self):
        r=self.board.result(claim_draw=True)
        if self.board.is_checkmate():
            w="Bot" if self.board.turn==self.human else "You"
            self.over_msg=f"Checkmate!\n{w} win!"
        elif self.board.is_stalemate(): self.over_msg="Stalemate!\nDraw"
        elif self.board.is_insufficient_material(): self.over_msg="Insufficient material\nDraw"
        elif self.board.can_claim_threefold_repetition(): self.over_msg="Threefold Repetition\nDraw"
        else: self.over_msg=f"Draw\n{r}"

    def build_review(self):
        counts={"brilliant":0,"great":0,"good":0,"best":0,"book":0,
                "inaccurate":0,"mistake":0,"miss":0,"blunder":0}
        for (san,badge,col,fen) in self.log:
            if col==self.human and badge in counts:
                counts[badge]+=1
        self.review=counts

# ── DRAWING ──────────────────────────────────────────────────────
def draw_eval(surf,gs,fonts):
    ex=EVAL_X; ey=BY; ew=EVAL_W; eh=BOARD_PX
    pygame.draw.rect(surf,(18,18,18),(ex-2,ey-2,ew+4,eh+4),border_radius=4)
    cl=max(-10,min(10,gs.eval_d))

    if gs.human == chess.WHITE:
        # Positive = White advantage → White fills bottom up
        white_h = int((cl + 10) / 20 * eh)
        black_h = eh - white_h
        pygame.draw.rect(surf, G_EVAL_B, (ex, ey, ew, black_h), border_radius=3)
        pygame.draw.rect(surf, G_EVAL_W, (ex, ey + black_h, ew, white_h), border_radius=3)
    else:
        # Negative = Black advantage → Black fills bottom up
        black_h = int((-cl + 10) / 20 * eh)
        white_h = eh - black_h
        pygame.draw.rect(surf, G_EVAL_W, (ex, ey, ew, white_h), border_radius=3)
        pygame.draw.rect(surf, G_EVAL_B, (ex, ey + white_h, ew, black_h), border_radius=3)

    mid_y = ey + eh // 2
    pygame.draw.line(surf,(90,90,90),(ex,mid_y),(ex+ew,mid_y),1)

    if abs(cl) < 0.3: lbl_str = "="
    elif cl > 0: lbl_str = f"+{cl:.1f}" if gs.human==chess.WHITE else f"-{cl:.1f}"
    else: lbl_str = f"{cl:.1f}" if gs.human==chess.WHITE else f"+{abs(cl):.1f}"
    lb=fonts["xs"].render(lbl_str,True,(130,130,130))
    surf.blit(lb,(ex,ey+eh+4))

def draw_board_game(surf,gs,pieces,fonts):
    flip=gs.flipped()
    disp_board = chess.Board(gs.log[gs.view_idx][3])
    
    for sq in chess.SQUARES:
        f=chess.square_file(sq); r=chess.square_rank(sq)
        x,y=gs.sq_px(sq,flip)
        pygame.draw.rect(surf,G_LIGHT_SQ if (f+r)%2==0 else G_DARK_SQ,(x,y,SQ,SQ))
        
    if not gs.is_viewing_history():
        if gs.last:
            for sq in [gs.last.from_square,gs.last.to_square]:
                x,y=gs.sq_px(sq,flip); hl=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
                hl.fill(G_LAST_MOVE); surf.blit(hl,(x,y))
        if disp_board.is_check():
            ksq=disp_board.king(disp_board.turn)
            if ksq:
                x,y=gs.sq_px(ksq,flip); hl=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
                hl.fill(G_CHECK); surf.blit(hl,(x,y))
        if gs.sel is not None:
            x,y=gs.sq_px(gs.sel,flip); hl=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
            hl.fill(G_HIGHLIGHT); surf.blit(hl,(x,y))
        if gs.hint_sq is not None and gs.hint_t>0:
            x,y=gs.sq_px(gs.hint_sq,flip); hl=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
            hl.fill((40,180,255,120)); surf.blit(hl,(x,y))
        for tgt in gs.targets:
            x,y=gs.sq_px(tgt,flip); ds=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
            if disp_board.piece_at(tgt):
                pygame.draw.circle(ds,(*G_ACCENT,80),(SQ//2,SQ//2),SQ//2-2,5)
            else:
                pygame.draw.circle(ds,(*G_ACCENT,60),(SQ//2,SQ//2),SQ//7)
            surf.blit(ds,(x,y))
            
    for sq in chess.SQUARES:
        pc=disp_board.piece_at(sq)
        if pc is None or (sq==gs.sel and not gs.is_viewing_history()): continue
        x,y=gs.sq_px(sq,flip); key=(pc.piece_type,pc.color)
        if key in pieces: surf.blit(pieces[key],(x,y))
        
    if gs.sel is not None and not gs.is_viewing_history():
        pc=disp_board.piece_at(gs.sel)
        if pc:
            x,y=gs.sq_px(gs.sel,flip); key=(pc.piece_type,pc.color)
            if key in pieces: surf.blit(pieces[key],(x,y))
            
    pygame.draw.rect(surf,G_ACCENT,(BX-2,BY-2,BOARD_PX+4,BOARD_PX+4),2,border_radius=2)
    cf=fonts["xs"]
    for i in range(8):
        fi=i if not flip else 7-i
        fc=G_DARK_SQ if (fi)%2==0 else G_LIGHT_SQ
        t=cf.render("abcdefgh"[i],True,fc)
        surf.blit(t,(BX+i*SQ+SQ-12,BY+BOARD_PX-13))
        ri=7-i if not flip else i
        rc=G_DARK_SQ if ri%2==1 else G_LIGHT_SQ
        t2=cf.render(str(ri+1),True,rc)
        surf.blit(t2,(BX+2,BY+i*SQ+2))

def draw_badge(surf,badge,sq,gs,fonts):
    if not badge or sq is None or gs.is_viewing_history(): return
    x,y=gs.sq_px(sq,gs.flipped())
    col=BADGE_COLS.get(badge,(200,200,200))
    sym=BADGE_SYM.get(badge,"")
    cs=pygame.Surface((26,26),pygame.SRCALPHA)
    pygame.draw.circle(cs,(*col,230),(13,13),13)
    surf.blit(cs,(x+SQ-22,y-4))
    t=fonts["badge"].render(sym,True,(255,255,255))
    surf.blit(t,(x+SQ-22+(26-t.get_width())//2,y-4+(26-t.get_height())//2))

def draw_panel(surf,gs,fonts,eval_bar_on=True):
    pygame.draw.rect(surf,G_PANEL_BG,(PANEL_X-4,0,PANEL_W+4,WIN_H))
    px=PANEL_X; pw=PANEL_W
    bot_col=gs.bot_col()

    # Clocks
    wt=gs.fmt_time(gs.white_t) if gs.use_timer else "\u221e"
    bt=gs.fmt_time(gs.black_t) if gs.use_timer else "\u221e"
    bot_clk=bt if bot_col==chess.BLACK else wt
    hum_clk=wt if gs.human==chess.WHITE else bt
    
    bc_active=(gs.board.turn==bot_col and gs.active_clock is not None)
    bc_col=G_ACCENT if bc_active else (70,70,70)
    pygame.draw.rect(surf,bc_col,(px,BY,pw-4,36),border_radius=6)
    ct=fonts["clock"].render(bot_clk,True,(255,255,255))
    surf.blit(ct,(px+pw//2-ct.get_width()//2,BY+8))
    bl=fonts["xs"].render(f"TOTEM  ELO {gs.elo}",True,(200,200,200))
    surf.blit(bl,(px+4,BY+1))
    
    hc_active=(gs.board.turn==gs.human and gs.active_clock is not None)
    hc_col=G_GREEN if hc_active else (70,70,70)
    pygame.draw.rect(surf,hc_col,(px,BY+BOARD_PX-36,pw-4,36),border_radius=6)
    ht=fonts["clock"].render(hum_clk,True,(255,255,255))
    surf.blit(ht,(px+pw//2-ht.get_width()//2,BY+BOARD_PX-28))
    hl2=fonts["xs"].render("You",True,(200,200,200))
    surf.blit(hl2,(px+4,BY+BOARD_PX-35))

    # Move Log
    log_top=BY+44; log_bot=BY+BOARD_PX-44
    log_h=log_bot-log_top
    surf.blit(fonts["sm"].render("MOVES",True,(140,140,140)),(px,log_top-18))
    
    moves_only = gs.log[1:] # Skip the "Start" dummy move
    pairs = [moves_only[i:i+2] for i in range(0, len(moves_only), 2)]
    
    visible_pairs = log_h // 20
    start_pair = max(0, len(pairs) - visible_pairs)
    
    for i, pair_idx in enumerate(range(start_pair, len(pairs))):
        pair = pairs[pair_idx]
        num = pair_idx + 1
        y_pos = log_top + i*20
        
        # Move Number
        lt=fonts["log"].render(f"{num}.",True,(120,120,120))
        surf.blit(lt,(px+4,y_pos))
        
        # White Move
        w_san, w_badge, _, _ = pair[0]
        w_col = BADGE_COLS.get(w_badge,(220,220,220))
        wt=fonts["log"].render(w_san,True,w_col)
        surf.blit(wt,(px + 45, y_pos))
        
        # Black Move
        if len(pair) > 1:
            b_san, b_badge, _, _ = pair[1]
            b_col = BADGE_COLS.get(b_badge,(220,220,220))
            bt=fonts["log"].render(b_san,True,b_col)
            surf.blit(bt,(px + 120, y_pos))

    # Navigation Buttons Area (bottom of panel)
    nav_y = log_bot - 10
    nav_w = pw // 5 - 4
    _draw_btn(surf, fonts, "|<", px, nav_y, nav_w, 24, G_BTN, (120,120,120))
    _draw_btn(surf, fonts, "<", px + nav_w + 2, nav_y, nav_w, 24, G_BTN, (120,120,120))
    _draw_btn(surf, fonts, "||", px + 2*nav_w + 4, nav_y, nav_w, 24, G_BTN, (120,120,120))
    _draw_btn(surf, fonts, ">", px + 3*nav_w + 6, nav_y, nav_w, 24, G_BTN, (120,120,120))
    _draw_btn(surf, fonts, ">|", px + 4*nav_w + 8, nav_y, nav_w, 24, G_BTN, (120,120,120))

    # Controls Area
    btn_y=BY+BOARD_PX+8
    if gs.mode==0 and not gs.over_msg:
        _draw_btn(surf,fonts,"\U0001f4a1 HINT",px,btn_y,pw//2-4,30,G_GOLD,(255,255,200))
        _draw_btn(surf,fonts,"RESIGN",px + pw//2,btn_y,pw//2-4,30,G_ACCENT,(255,200,200))
    elif not gs.over_msg:
        _draw_btn(surf,fonts,"RESIGN",px,btn_y,pw-4,30,G_ACCENT,(255,200,200))
        
    if gs.over_msg or gs.mode==2:
        _draw_btn(surf,fonts,"\U0001f4ca GAME REVIEW",px,btn_y+36,pw-4,32,G_ACCENT2,(200,230,255))
        
    # Eval bar toggle + Home Button
    toggle_y=btn_y+74
    _draw_toggle(surf,fonts,"Evaluation Bar",px,toggle_y,pw-40,eval_bar_on)
    _draw_btn(surf,fonts,"HOME",px + pw - 60,toggle_y, 56, 26, (40,40,40), (120,120,120))

    if gs.over_msg:
        ow=pw-4; oh=64
        os2=pygame.Surface((ow,oh),pygame.SRCALPHA); os2.fill((0,0,0,180))
        surf.blit(os2,(px,WIN_H//2-32))
        for li,line in enumerate(gs.over_msg.split("\n")):
            t=fonts["med"].render(line,True,G_ACCENT)
            surf.blit(t,(px+ow//2-t.get_width()//2,WIN_H//2-24+li*26))

def _draw_btn(surf,fonts,label,x,y,w,h,col,tcol):
    mx,my=pygame.mouse.get_pos()
    hov=x<=mx<=x+w and y<=my<=y+h
    pygame.draw.rect(surf,(min(col[0]+30,255),min(col[1]+30,255),min(col[2]+30,255)) if hov else col,
                     (x,y,w,h),border_radius=4)
    pygame.draw.rect(surf,tcol,(x,y,w,h),1,border_radius=4)
    t=fonts["sm"].render(label,True,(255,255,255))
    surf.blit(t,(x+w//2-t.get_width()//2,y+h//2-t.get_height()//2))

def _draw_toggle(surf,fonts,label,x,y,w,on):
    lbl=fonts["xs"].render(label,True,(160,160,160))
    surf.blit(lbl,(x+4,y+5))
    tw=42; th=22; tx=x+w-tw-2; ty=y+2
    track_col=(0,188,100) if on else (60,60,60)
    pygame.draw.rect(surf,track_col,(tx,ty,tw,th),border_radius=11)
    pygame.draw.rect(surf,(120,120,120),(tx,ty,tw,th),1,border_radius=11)
    thumb_x=tx+tw-13 if on else tx+3
    pygame.draw.circle(surf,(240,240,240),(thumb_x+8,ty+th//2),9)

def draw_review_overlay(surf,gs,fonts):
    if gs.review is None: return
    ow=540; oh=400
    ox=(WIN_W-ow)//2; oy=(WIN_H-oh)//2
    bg=pygame.Surface((ow,oh),pygame.SRCALPHA); bg.fill((18,18,18,240))
    surf.blit(bg,(ox,oy))
    pygame.draw.rect(surf,G_ACCENT2,(ox,oy,ow,oh),2,border_radius=12)
    t=fonts["med"].render("GAME REVIEW",True,G_ACCENT2)
    surf.blit(t,(ox+ow//2-t.get_width()//2,oy+12))
    pygame.draw.line(surf,(60,60,60),(ox+20,oy+44),(ox+ow-20,oy+44),1)
    cols2=list(BADGE_COLS.items())
    for i,(badge,col) in enumerate(cols2):
        cnt=gs.review.get(badge,0)
        row=i//2; c2=i%2
        bx=ox+30+c2*260; by2=oy+60+row*52
        cs=pygame.Surface((28,28),pygame.SRCALPHA)
        pygame.draw.circle(cs,(*col,220),(14,14),14)
        surf.blit(cs,(bx,by2+2))
        sym=BADGE_SYM.get(badge,"")
        st=fonts["badge"].render(sym,True,(255,255,255))
        surf.blit(st,(bx+14-st.get_width()//2,by2+14-st.get_height()//2))
        lt=fonts["sm"].render(badge.capitalize(),True,col)
        surf.blit(lt,(bx+36,by2+2))
        ct2=fonts["med"].render(str(cnt),True,(220,220,220))
        surf.blit(ct2,(bx+36,by2+20))
    cx=ox+ow-36; cy=oy+8
    pygame.draw.circle(surf,(60,60,60),(cx,cy),12)
    pygame.draw.circle(surf,G_ACCENT,(cx,cy),12,2)
    xt=fonts["sm"].render("✕",True,(200,200,200))
    surf.blit(xt,(cx-xt.get_width()//2,cy-xt.get_height()//2))

def draw_promo_menu(surf,gs,pieces,fonts):
    if gs.promo is None: return
    pcs=[chess.QUEEN,chess.ROOK,chess.BISHOP,chess.KNIGHT]
    ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,150)); surf.blit(ov,(0,0))
    bw,bh=300,84; bx=WIN_W//2-bw//2; by=WIN_H//2-bh//2
    pygame.draw.rect(surf,(30,30,30),(bx,by,bw,bh),border_radius=10)
    pygame.draw.rect(surf,G_ACCENT,(bx,by,bw,bh),2,border_radius=10)
    t=fonts["sm"].render("PROMOTE TO:",True,(200,200,200))
    surf.blit(t,(bx+bw//2-t.get_width()//2,by+6))
    sz=58; total=len(pcs)*sz+(len(pcs)-1)*4; sx=bx+(bw-total)//2
    for i,pt in enumerate(pcs):
        px2=sx+i*(sz+4); py2=by+84-sz-4
        mx,my=pygame.mouse.get_pos()
        hov=px2<=mx<=px2+sz and py2<=my<=py2+sz
        pygame.draw.rect(surf,(80,80,80) if hov else (50,50,50),(px2,py2,sz,sz),border_radius=6)
        key=(pt,gs.human)
        if key in pieces:
            surf.blit(pygame.transform.scale(pieces[key],(sz,sz)),(px2,py2))

# ── FONTS ────────────────────────────────────────────────────────
def make_fonts():
    title_name = "bahnschrift"
    return {
        "big":   pygame.font.SysFont(title_name, 34, bold=True),
        "med":   pygame.font.SysFont("segoeui",  16, bold=True),
        "sm":    pygame.font.SysFont("segoeui",  13, bold=False),
        "xs":    pygame.font.SysFont("consolas", 11, bold=True),
        "elo":   pygame.font.SysFont(title_name, 40, bold=True),
        "btn":   pygame.font.SysFont("segoeui",  18, bold=True),
        "log":   pygame.font.SysFont("segoeui", 14, bold=True),
        "badge": pygame.font.SysFont("segoeui",  10, bold=True),
        "clock": pygame.font.SysFont("consolas", 18, bold=True),
    }

# ── LOBBY RUNNER ─────────────────────────────────────────────────
def run_lobby(screen,clock,fonts,pieces):
    lobby=Lobby(fonts,pieces)
    
    inputting_fen = False
    fen_text = ""
    error_msg = ""
    
    while True:
        dt=clock.tick(FPS)/1000.0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            
            # FEN Input Logic
            if inputting_fen:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        inputting_fen = False
                        error_msg = ""
                    elif ev.key == pygame.K_RETURN:
                        try:
                            chess.Board(fen_text) # Test if valid FEN
                            return lobby.elo, lobby.time_idx, lobby.mode_idx, fen_text.strip()
                        except ValueError:
                            error_msg = "Invalid FEN String!"
                    elif ev.key == pygame.K_BACKSPACE:
                        fen_text = fen_text[:-1]
                        error_msg = ""
                    # Safe clipboard paste check compatible with all OS
                    elif ev.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL or pygame.key.get_mods() & pygame.KMOD_META):
                        try: 
                            clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                            if clip: 
                                if isinstance(clip, bytes):
                                    fen_text += clip.decode('utf-8', errors='ignore').replace('\x00', '').strip()
                                else:
                                    fen_text += str(clip).replace('\x00', '').strip()
                        except: 
                            pass
                    else:
                        if ev.unicode and ev.unicode.isprintable():
                            fen_text += ev.unicode
                            error_msg = ""
            else:
                action = lobby.hit(ev)
                if action == "play":
                    return lobby.elo, lobby.time_idx, lobby.mode_idx, None
                elif action == "fen":
                    inputting_fen = True
                    fen_text = ""
                    error_msg = ""
                    
        lobby.draw(screen,dt)
        
        # FEN Overlay Draw
        if inputting_fen:
            ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            ov.fill((0,0,0,210))
            screen.blit(ov, (0,0))
            
            bx, by, bw, bh = WIN_W//2 - 250, WIN_H//2 - 90, 500, 180
            pygame.draw.rect(screen, (35,35,35), (bx, by, bw, bh), border_radius=10)
            pygame.draw.rect(screen, G_ACCENT, (bx, by, bw, bh), 2, border_radius=10)
            
            t1 = fonts["med"].render("ENTER CUSTOM FEN STRING", True, (255,255,255))
            screen.blit(t1, (bx + bw//2 - t1.get_width()//2, by + 20))
            
            pygame.draw.rect(screen, (15,15,15), (bx+20, by+60, bw-40, 40), border_radius=5)
            pygame.draw.rect(screen, (100,100,100), (bx+20, by+60, bw-40, 40), 1, border_radius=5)
            
            disp_txt = fen_text if len(fen_text) < 55 else "..." + fen_text[-52:]
            t2 = fonts["xs"].render(disp_txt + "_", True, (200,200,200))
            screen.blit(t2, (bx+30, by+72))
            
            t3 = fonts["sm"].render("Press ENTER to start | ESC to cancel | Ctrl+V to paste", True, (140,140,140))
            screen.blit(t3, (bx + bw//2 - t3.get_width()//2, by + 120))
            
            if error_msg:
                t4 = fonts["sm"].render(error_msg, True, (255,80,80))
                screen.blit(t4, (bx + bw//2 - t4.get_width()//2, by + 150))
                
        pygame.display.flip()

# ── MAIN GAME LOOP ───────────────────────────────────────────────
def run_game(screen,clock,fonts,pieces,elo,time_idx,mode_idx, start_fen=None):
    time_sec=TIME_OPTIONS[time_idx][1]
    gs=GS(elo,time_sec,mode_idx, start_fen)
    show_review=False
    eval_bar_on=True

    while True:
        dt=clock.tick(FPS)/1000.0
        tgt=max(-10,min(10,gs.eval_s/100))
        gs.eval_d+=(tgt-gs.eval_d)*min(1.0,dt*4)
        
        if gs.badge_t>0:
            gs.badge_t-=dt
            if gs.badge_t<=0: gs.badge=""; gs.badge_sq=None
            
        if gs.hint_t>0:
            gs.hint_t-=dt
            if gs.hint_t<=0: gs.hint_sq=None
            
        gs.tick_clock()
        bot=gs.bot_col()
        
        if not gs.over_msg and gs.board.turn==bot and not gs.thinking and not gs.is_viewing_history():
            gs.thinking=True
            gs.think_t=time.time()
            
        if gs.thinking and time.time()-gs.think_t>=0.15:
            think_elapsed = time.time() - gs.think_t
            m=gs.engine.move(gs.board)
      
            if m:
                if gs.use_timer:
                    if gs.active_clock is None:
                        gs.active_clock = chess.WHITE
                    elif bot == chess.WHITE:
                        gs.white_t = max(0.0, gs.white_t - think_elapsed)
                    else:
                        gs.black_t = max(0.0, gs.black_t - think_elapsed)
                    gs.last_tick = time.time()
                gs.do_move(m,False)
            gs.thinking=False

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_r:
                return "lobby"

            if show_review and ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=ev.pos
                ow=540; oh=400; ox=(WIN_W-ow)//2; oy=(WIN_H-oh)//2
                cx=ox+ow-36; cy=oy+8
                if math.hypot(mx-cx,my-cy)<=14:
                    show_review=False; continue

            if ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=ev.pos
                px = PANEL_X
                pw = PANEL_W
                btn_y=BY+BOARD_PX+8
                
                toggle_y=btn_y+74
                if px<=mx<=px+pw-40 and toggle_y<=my<=toggle_y+26:
                    eval_bar_on=not eval_bar_on
                if px+pw-60<=mx<=px+pw and toggle_y<=my<=toggle_y+26:
                    return "lobby" 

                if not gs.over_msg:
                    if gs.mode==0:
                        if px<=mx<=px+pw//2-4 and btn_y<=my<=btn_y+30:
                            hm=gs.engine.best_in_pos(gs.board)
                            if hm: gs.hint_sq=hm.to_square; gs.hint_t=3.0
                        if px+pw//2<=mx<=px+pw and btn_y<=my<=btn_y+30:
                            gs.over_msg="Resigned\nBot wins"
                    else:
                        if px<=mx<=px+pw-4 and btn_y<=my<=btn_y+30:
                            gs.over_msg="Resigned\nBot wins"
                            
                log_bot=BY+BOARD_PX-44
                nav_y = log_bot - 10
                nav_w = pw // 5 - 4
                if nav_y <= my <= nav_y + 24:
                    if px <= mx <= px + nav_w: gs.view_idx = 0           
                    elif px + nav_w <= mx <= px + 2*nav_w: gs.view_idx = max(0, gs.view_idx - 1)
                    elif px + 2*nav_w <= mx <= px + 3*nav_w: gs.view_idx = len(gs.log) - 1
                    elif px + 3*nav_w <= mx <= px + 4*nav_w: gs.view_idx = min(len(gs.log) - 1, gs.view_idx + 1)
                    elif px + 4*nav_w <= mx <= px + 5*nav_w: gs.view_idx = len(gs.log) - 1 
     
                if (gs.over_msg or gs.mode==2):
                    if px<=mx<=px+pw-4 and btn_y+36<=my<=btn_y+68:
                        gs.build_review(); show_review=True

            if gs.promo and ev.type==pygame.MOUSEBUTTONDOWN:
                pcs=[chess.QUEEN,chess.ROOK,chess.BISHOP,chess.KNIGHT]
                sz=58; bw=300; bx=WIN_W//2-bw//2; by=WIN_H//2-42
                total=len(pcs)*sz+(len(pcs)-1)*4; sx=bx+(bw-total)//2
                mx,my=ev.pos
                for i,pt in enumerate(pcs):
                    px2=sx+i*(sz+4); py2=by+84-sz-4
                    if px2<=mx<=px2+sz and py2<=my<=py2+sz:
                        frm,to=gs.promo
                        mv=chess.Move(frm,to,promotion=pt)
                        if mv in gs.board.legal_moves: gs.do_move(mv,True)
                        gs.promo=None; break
                continue

            if (ev.type==pygame.MOUSEBUTTONDOWN and gs.board.turn==gs.human
                    and not gs.over_msg and not gs.promo and not show_review and not gs.is_viewing_history()):
              
                mx,my=ev.pos
                sq=gs.px_sq(mx,my,gs.flipped())
                if sq is None: gs.sel=None; gs.targets=[]; continue
                if gs.sel is None:
                    pc=gs.board.piece_at(sq)
                    if pc and pc.color==gs.human:
                        gs.sel=sq
                        gs.targets=[m.to_square for m in gs.board.legal_moves if m.from_square==sq]
                else:
                    if sq in gs.targets:
                        pc=gs.board.piece_at(gs.sel)
                        promo=pc and pc.piece_type==chess.PAWN and chess.square_rank(sq) in (0,7)
                        if promo: gs.promo=(gs.sel,sq)
                        else:
                            mv=chess.Move(gs.sel,sq)
                            if mv in gs.board.legal_moves:
                                if gs.use_timer and gs.active_clock is None:
                                    gs.active_clock = chess.WHITE  
                                    gs.last_tick = time.time()
                                gs.do_move(mv,True)
                        gs.sel=None; gs.targets=[]
                    elif gs.board.piece_at(sq) and gs.board.piece_at(sq).color==gs.human:
                        gs.sel=sq
                        gs.targets=[m.to_square for m in gs.board.legal_moves if m.from_square==sq]
                    else: gs.sel=None; gs.targets=[]

        screen.fill(G_BG)
        title_str = "T O T E M   -   T H E   C H E S S   B O T"
        t=fonts["big"].render(title_str, True, (0, 188, 212))   
        ts=fonts["big"].render(title_str, True, (0, 60, 80))
        screen.blit(ts,(BX+2, 14))
        screen.blit(t,  (BX,   12))
        ms=f"{'White' if gs.human==chess.WHITE else 'Black'} \u2022 {MODES[gs.mode]} \u2022 {TIME_OPTIONS[time_idx][0]}  |  Press 'R' for lobby"
        screen.blit(fonts["xs"].render(ms,True,(255, 255, 255)),(BX,WIN_H-18))

        if eval_bar_on: draw_eval(screen,gs,fonts)
        draw_board_game(screen,gs,pieces,fonts)
        draw_badge(screen,gs.badge,gs.badge_sq,gs,fonts)
        draw_panel(screen,gs,fonts,eval_bar_on)
        if gs.promo: draw_promo_menu(screen,gs,pieces,fonts)
        if show_review: draw_review_overlay(screen,gs,fonts)

        pygame.display.flip()

# ── ENTRY ────────────────────────────────────────────────────────
def main():
    pygame.init()
    
    # Create the window FIRST before initializing the clipboard
    screen=pygame.display.set_mode((WIN_W,WIN_H))
    pygame.display.set_caption("TOTEM - The Chess Bot")
    clock=pygame.time.Clock()
    
    # Safely initialize the clipboard feature for Ctrl+V
    try: 
        pygame.scrap.init()
        if hasattr(pygame.scrap, 'set_mode'):
            pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
    except: 
        pass 
        
    fonts=make_fonts(); pieces=make_pieces(SQ)
    
    # Tournament hook check: No UI, purely executes next_move(fen)
    if len(sys.argv) > 1 and "fen" in sys.argv[1].lower():
        fen = sys.argv[2] if len(sys.argv) > 2 else chess.STARTING_FEN
        print(next_move(fen))
        sys.exit(0)

    # Launch full UI Game Arena
    while True:
        elo,time_idx,mode_idx, start_fen = run_lobby(screen,clock,fonts,pieces)
        result=run_game(screen,clock,fonts,pieces,elo,time_idx,mode_idx, start_fen)

if __name__=="__main__":
    main()