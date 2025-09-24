import copy
import random
from typing import List, Tuple, Optional

# Constantes de colores
EMPTY = 0
BLACK = 1
WHITE = -1

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# ------------------
# Funciones auxiliares
# ------------------
def move_to_coords(move: str):
    """Convierte 'd3' -> (row, col). 'pass' -> None"""
    if not move:
        return None
    m = move.strip().lower()
    if m == "pass":
        return None
    col = ord(m[0]) - ord('a')
    row = int(m[1]) - 1
    return (row, col)

def coords_to_move(r: int, c: int):
    return f"{chr(ord('a')+c)}{r+1}"

# ------------------
# Clase Board
# ------------------
class Board:
    def __init__(self):
        self.b = [[EMPTY]*8 for _ in range(8)]
        self.b[3][3] = WHITE
        self.b[3][4] = BLACK
        self.b[4][3] = BLACK
        self.b[4][4] = WHITE

    def copy(self):
        nb = Board()
        nb.b = [row[:] for row in self.b]
        return nb

    def inside(self, r,c): return 0 <= r < 8 and 0 <= c < 8

    def _flips_in_dir(self,r,c,player,dr,dc):
        flips = []
        r += dr; c += dc
        while self.inside(r,c) and self.b[r][c] == -player:
            flips.append((r,c))
            r += dr; c += dc
        if self.inside(r,c) and self.b[r][c]==player and flips:
            return flips
        return []

    def legal_moves_coords(self, player:int):
        moves=[]
        for r in range(8):
            for c in range(8):
                if self.b[r][c]!=EMPTY: continue
                total=[]
                for dr,dc in DIRECTIONS:
                    f=self._flips_in_dir(r,c,player,dr,dc)
                    if f: total.extend(f)
                if total: moves.append((r,c))
        return moves

    def legal_moves(self, player:int):
        return [coords_to_move(r,c) for r,c in self.legal_moves_coords(player)]

    def apply_move_coords(self, r:int, c:int, player:int):
        flips_total=[]
        for dr,dc in DIRECTIONS:
            f=self._flips_in_dir(r,c,player,dr,dc)
            if f: flips_total.extend(f)
        if not flips_total: return False
        self.b[r][c] = player
        for fr,fc in flips_total:
            self.b[fr][fc] = player
        return True

    def apply_move(self, move:str, player:int):
        if not move: return False
        if move.lower()=="pass": return True
        coords=move_to_coords(move)
        if coords is None: return False
        r,c=coords
        return self.apply_move_coords(r,c,player)

    def has_any_move(self, player:int):
        return len(self.legal_moves_coords(player))>0

    def is_terminal(self):
        return not (self.has_any_move(BLACK) or self.has_any_move(WHITE))

    def counts(self):
        b=sum(1 for r in range(8) for c in range(8) if self.b[r][c]==BLACK)
        w=sum(1 for r in range(8) for c in range(8) if self.b[r][c]==WHITE)
        return {"black":b,"white":w}

    def evaluate(self):
        cnt=self.counts()
        disc_diff=cnt["black"]-cnt["white"]
        corners=[(0,0),(0,7),(7,0),(7,7)]
        corner_score=0
        for r,c in corners:
            v=self.b[r][c]
            if v==BLACK: corner_score+=25
            elif v==WHITE: corner_score-=25
        mobility=len(self.legal_moves_coords(BLACK))-len(self.legal_moves_coords(WHITE))
        return disc_diff + 10*mobility + corner_score

    def to_matrix(self):
        return [row[:] for row in self.b]

# ------------------
# Motor Negamax
# ------------------
def negamax(board:Board, depth:int, player:int, alpha:float, beta:float):
    if depth==0 or board.is_terminal():
        val=player*board.evaluate()
        return val,None,[]
    moves_coords=board.legal_moves_coords(player)
    if not moves_coords:
        if board.has_any_move(-player):
            val,mv,pv=negamax(board,depth-1,-player,-beta,-alpha)
            return -val,None,pv
        else:
            return player*board.evaluate(),None,[]
    best_val=-1e9
    best_move=None
    best_pv=[]
    for r,c in moves_coords:
        nb=board.copy()
        nb.apply_move_coords(r,c,player)
        child_val,_,child_pv=negamax(nb,depth-1,-player,-beta,-alpha)
        val=-child_val
        if val>best_val:
            best_val=val
            best_move=(r,c)
            best_pv=[coords_to_move(r,c)]+child_pv
        alpha=max(alpha,val)
        if alpha>=beta: break
    return best_val,best_move,best_pv

def find_best_move(board:Board, player:int, max_depth:int=3):
    val,best_coords,pv=negamax(board,max_depth,player,-1e9,1e9)
    if best_coords is None: return None,pv,val
    r,c=best_coords
    return coords_to_move(r,c),pv,val

# ------------------
# Clase Engine interactivo
# ------------------
class OthelloEngineInteractive:
    def __init__(self):
        self.board=Board()
        self.current_color=BLACK

    def get_legal_moves(self):
        return self.board.legal_moves(self.current_color)

    def apply_move(self, move:str):
        ok=self.board.apply_move(move,self.current_color)
        if ok:
            self.current_color=-self.current_color
        return ok

    def get_pv(self, max_depth=3):
        best_move, pv_list, _ = find_best_move(self.board, self.current_color, max_depth=max_depth)
        if best_move is None:
            return pv_list
        if pv_list and pv_list[0]==best_move:
            return pv_list
        return [best_move] + pv_list

