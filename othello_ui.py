import copy
import random
from typing import List, Tuple, Optional

# Constantes
EMPTY = 0
BLACK = 1
WHITE = -1
DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def move_to_coords(move: str):
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

# ---------------------------
# Clase principal
class OthelloEngine:
    def __init__(self):
        self.board = Board()
        self.current_color = BLACK
        self.last_flips = []

    # ----------------------
    # Board interface
    def get_board(self):
        mat = self.board.to_matrix()
        # Convertir a caracteres
        return [["B" if c==BLACK else "W" if c==WHITE else "." for c in row] for row in mat]

    def legal_moves(self, color: int):
        return self.board.legal_moves(color)

    def apply_move(self, color: int, move: str):
        if move.lower() == "pass":
            self.last_flips = []
            return True
        coords = move_to_coords(move)
        if coords is None:
            return False
        r,c = coords
        flips_before = sum(row[:] for row in self.board.b)
        ok = self.board.apply_move_coords(r,c,color)
        # Guardar últimos flips
        self.last_flips = [(r,c) for r in range(8) for c in range(8)
                           if self.board.b[r][c] == color]
        return ok

    def pass_turn(self):
        self.current_color = -self.current_color

    def is_game_over(self):
        return self.board.is_terminal()

    def get_result(self):
        counts = self.board.counts()
        if counts["black"] > counts["white"]:
            return "Black gana"
        elif counts["white"] > counts["black"]:
            return "White gana"
        else:
            return "Empate"

    # ----------------------
    # Motor de decisión
    def find_best_move(self, board=None, player=None, max_depth: int=4):
        b = board or self.board
        p = player or self.current_color
        return find_best_move(b, p, max_depth)

    def get_pv(self, max_depth=3):
        _, pv, _ = self.find_best_move(self.board, self.current_color, max_depth)
        return pv

# ---------------------------
# Board y funciones auxiliares
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

    def inside(self, r, c): return 0<=r<8 and 0<=c<8

    def _flips_in_dir(self, r,c,player,dr,dc):
        flips=[]
        r+=dr;c+=dc
        while self.inside(r,c) and self.b[r][c]==-player:
            flips.append((r,c))
            r+=dr;c+=dc
        if self.inside(r,c) and self.b[r][c]==player and flips:
            return flips
        return []

    def legal_moves_coords(self, player:int):
        moves=[]
        for r in range(8):
            for c in range(8):
                if self.b[r][c]!=EMPTY: continue
                flips_total=[]
                for dr,dc in DIRECTIONS:
                    flips_total.extend(self._flips_in_dir(r,c,player,dr,dc))
                if flips_total: moves.append((r,c))
        return moves

    def legal_moves(self, player:int):
        return [coords_to_move(r,c) for r,c in self.legal_moves_coords(player)]

    def apply_move_coords(self,r:int,c:int,player:int):
        flips_total=[]
        for dr,dc in DIRECTIONS:
            flips_total.extend(self._flips_in_dir(r,c,player,dr,dc))
        if not flips_total: return False
        self.b[r][c]=player
        for fr,fc in flips_total: self.b[fr][fc]=player
        return True

    def has_any_move(self,player:int): return bool(self.legal_moves_coords(player))
    def is_terminal(self): return not (self.has_any_move(BLACK) or self.has_any_move(WHITE))
    def counts(self):
        return {"black": sum(r.count(BLACK) for r in self.b),
                "white": sum(r.count(WHITE) for r in self.b)}
    def to_matrix(self): return [row[:] for row in self.b]

# ---------------------------
# Negamax con alpha-beta
def negamax(board: Board, depth:int, player:int, alpha:float, beta:float):
    if depth==0 or board.is_terminal(): return (player*board.evaluate(), None, [])
    moves_coords=board.legal_moves_coords(player)
    if not moves_coords:
        if board.has_any_move(-player):
            val,mv,pv=negamax(board,depth-1,-player,-beta,-alpha)
            return (-val,None,pv)
        else: return (player*board.evaluate(), None, [])
    best_val=-1e9; best_move=None; best_pv=[]
    for r,c in moves_coords:
        nb=board.copy()
        nb.apply_move_coords(r,c,player)
        val_child, _, pv_child = negamax(nb, depth-1, -player, -beta, -alpha)
        val=-val_child
        if val>best_val:
            best_val=val
            best_move=(r,c)
            best_pv=[coords_to_move(r,c)]+pv_child
        alpha=max(alpha,val)
        if alpha>=beta: break
    return (best_val,best_move,best_pv)

def find_best_move(board: Board, player:int, max_depth:int=4):
    val, best_coords, pv = negamax(board,max_depth,player,-1e9,1e9)
    if best_coords is None: return (None,pv,val)
    r,c=best_coords
    return (coords_to_move(r,c), pv, val)

# ---------------------------
# Compatibilidad global
def analyze_game(moves:List[str], max_depth:int=4):
    engine = OthelloEngine()
    return analyze_game_module(moves, engine, max_depth)

def analyze_game_module(moves:List[str], engine:OthelloEngine, max_depth:int=4):
    # aquí puedes usar la función analyze_game original
    return {"analysis": [], "summary": {"moves_count":len(moves)}}
