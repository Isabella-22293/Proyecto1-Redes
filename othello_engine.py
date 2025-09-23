import copy
import random
from typing import List, Tuple, Optional

EMPTY = 0
BLACK = 1
WHITE = -1

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

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

class Board:
    def __init__(self):
        # 8x8 matrix, row 0 = top
        self.b = [[EMPTY]*8 for _ in range(8)]
        # initial Othello position
        self.b[3][3] = WHITE
        self.b[3][4] = BLACK
        self.b[4][3] = BLACK
        self.b[4][4] = WHITE

    def copy(self):
        nb = Board()
        nb.b = [row[:] for row in self.b]
        return nb

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def _flips_in_dir(self, r, c, player, dr, dc):
        flips = []
        r += dr; c += dc
        while self.inside(r, c) and self.b[r][c] == -player:
            flips.append((r, c))
            r += dr; c += dc
        if self.inside(r, c) and self.b[r][c] == player and flips:
            return flips
        return []

    def legal_moves_coords(self, player: int):
        moves = []
        for r in range(8):
            for c in range(8):
                if self.b[r][c] != EMPTY:
                    continue
                total_flips = []
                for dr, dc in DIRECTIONS:
                    f = self._flips_in_dir(r, c, player, dr, dc)
                    if f:
                        total_flips.extend(f)
                if total_flips:
                    moves.append((r, c))
        return moves

    def legal_moves(self, player:int):
        return [coords_to_move(r,c) for (r,c) in self.legal_moves_coords(player)]

    def apply_move_coords(self, r: int, c: int, player: int):
        """Aplica el movimiento (r,c) y voltea fichas. Devuelve True si fue válido."""
        flips_total = []
        for dr, dc in DIRECTIONS:
            flips = self._flips_in_dir(r, c, player, dr, dc)
            if flips:
                flips_total.extend(flips)
        if not flips_total:
            return False
        self.b[r][c] = player
        for (fr, fc) in flips_total:
            self.b[fr][fc] = player
        return True

    def apply_move(self, move: str, player: int):
        if not move:
            return False
        if move.lower() == "pass":
            return True
        coords = move_to_coords(move)
        if coords is None:
            return False
        r, c = coords
        return self.apply_move_coords(r, c, player)

    def has_any_move(self, player:int):
        return len(self.legal_moves_coords(player)) > 0

    def is_terminal(self):
        return not (self.has_any_move(BLACK) or self.has_any_move(WHITE))

    def counts(self):
        b = sum(1 for r in range(8) for c in range(8) if self.b[r][c] == BLACK)
        w = sum(1 for r in range(8) for c in range(8) if self.b[r][c] == WHITE)
        return {"black": b, "white": w}

    def evaluate(self):
        """
        Heurística (desde la perspectiva BLACK):
        - diferencia de fichas
        - valor fuerte a esquinas
        - movilidad
        """
        cnt = self.counts()
        disc_diff = cnt["black"] - cnt["white"]

        # corner occupancy
        corners = [(0,0),(0,7),(7,0),(7,7)]
        corner_score = 0
        for (r,c) in corners:
            v = self.b[r][c]
            if v == BLACK: corner_score += 25
            elif v == WHITE: corner_score -= 25

        mobility = len(self.legal_moves_coords(BLACK)) - len(self.legal_moves_coords(WHITE))

        score = disc_diff + 10 * mobility + corner_score
        return score

    def to_matrix(self):
        """Devuelve la matriz 8x8 con 1 = black, -1 = white, 0 empty"""
        return [row[:] for row in self.b]

# Negamax with alpha-beta, returns tuple (value, best_move_coords, pv_list)
def negamax(board: Board, depth: int, player: int, alpha: float, beta: float):
    if depth == 0 or board.is_terminal():
        val = player * board.evaluate()
        return (val, None, [])
    moves_coords = board.legal_moves_coords(player)
    if not moves_coords:
        # pass turn
        if board.has_any_move(-player):
            val, mv, pv = negamax(board, depth, -player, -beta, -alpha)
            return (-val, None, pv)
        else:
            val = player * board.evaluate()
            return (val, None, [])
    best_val = -1e9
    best_move = None
    best_pv = []
    for (r,c) in moves_coords:
        nb = board.copy()
        nb.apply_move_coords(r,c,player)
        child_val, _, child_pv = negamax(nb, depth-1, -player, -beta, -alpha)
        val = -child_val
        if val > best_val:
            best_val = val
            best_move = (r,c)
            best_pv = [coords_to_move(r,c)] + child_pv
        alpha = max(alpha, val)
        if alpha >= beta:
            break
    return (best_val, best_move, best_pv)

def find_best_move(board: Board, player: int, max_depth: int=4):
    val, best_coords, pv = negamax(board, max_depth, player, -1e9, 1e9)
    if best_coords is None:
        return (None, pv, val)
    r,c = best_coords
    return (coords_to_move(r,c), pv, val)

def board_after_moves(moves: List[str]):
    b = Board()
    player = BLACK
    for m in moves:
        if m and m.lower()=="pass":
            player = -player
            continue
        coords = move_to_coords(m)
        if coords is None:
            player = -player
            continue
        r,c = coords
        ok = b.apply_move_coords(r,c,player)
        if not ok:
            # movimiento inválido: lanzar excepción clara
            raise ValueError(f"Movimiento inválido en secuencia: {m} (r={r},c={c})")
        player = -player
    return b.to_matrix()

def analyze_game(moves: List[str], max_depth: int=4, error_threshold: float=3.0):
    """
    Para cada jugada en `moves`, calcula la mejor jugada según el motor
    y marca si la jugada real es un error (según heuristic diff).
    Devuelve estructura con lista de análisis por jugada y resumen.
    """
    b = Board()
    analysis = []
    player = BLACK  # black starts
    errors_count = 0
    first_error = None

    for i, actual_move in enumerate(moves):
        # best move from this position
        best_move, pv, best_val = find_best_move(b, player, max_depth=max_depth)
        # simulate applying best and actual (to get heuristic)
        # compute eval after best_move
        eval_best = None
        eval_actual = None

        # simulation for best
        if best_move is None:
            # best is pass
            nb = b.copy()
            # pass does not change board
            eval_best = player * nb.evaluate()
        else:
            nb = b.copy()
            nb.apply_move(best_move, player)
            eval_best = player * nb.evaluate()

        # simulation for actual
        if actual_move is None or (isinstance(actual_move, str) and actual_move.strip().lower()=="pass"):
            na = b.copy()
            eval_actual = player * na.evaluate()
        else:
            na = b.copy()
            try:
                na.apply_move(actual_move, player)
                eval_actual = player * na.evaluate()
            except Exception:
                # movimiento inválido: lo marcamos y seguimos
                eval_actual = player * b.evaluate()

        score_diff = (eval_best - eval_actual) if (eval_best is not None and eval_actual is not None) else 0.0
        is_error = score_diff >= error_threshold

        explanation = ""
        if is_error:
            errors_count += 1
            if first_error is None:
                first_error = i

            # heurísticas simples para explicar:
            #  - si después de la jugada real el oponente tiene una esquina y con la mejor jugada no
            opponent = -player
            na_after_actual = na
            nb_after_best = nb

            opp_moves_after_actual = na_after_actual.legal_moves(opponent)
            opp_moves_after_best = nb_after_best.legal_moves(opponent)
            corners = {"a1","a8","h1","h8"}
            if any(c in opp_moves_after_actual for c in corners) and not any(c in opp_moves_after_best for c in corners):
                explanation = "La jugada permite que el oponente capture una esquina en la siguiente jugada."
            else:
                # si la jugada usada voltea muchas menos fichas que la mejor, mencionarlo
                # contar voltees aproximadas: compare disc diff
                if eval_best - eval_actual >= 8:
                    explanation = "Movimiento grave: la heurística muestra pérdida significativa de ventaja."
                else:
                    explanation = "Movimiento subóptimo según el motor."

        analysis.append({
            "move_index": i,
            "player": "black" if player==BLACK else "white",
            "move": actual_move,
            "engine_best": best_move,
            "pv": pv,
            "score_after_best_from_player_perspective": eval_best,
            "score_after_actual_from_player_perspective": eval_actual,
            "score_diff": score_diff,
            "is_error": bool(is_error),
            "explanation": explanation
        })

        # apply actual move to board (even if flagged como error)
        if actual_move and str(actual_move).strip().lower()!="pass":
            b.apply_move(actual_move, player)
        # alternate player
        player = -player

    summary = {
        "moves_count": len(moves),
        "errors_count": errors_count,
        "first_error_index": first_error
    }
    return {"analysis": analysis, "summary": summary}

def generate_random_game():
    """Genera una partida legal completa jugando aleatoriamente."""
    b = Board()
    moves = []
    player = BLACK
    while not b.is_terminal():
        moves_coords = b.legal_moves_coords(player)
        if not moves_coords:
            moves.append("pass")
            player = -player
            continue
        r,c = random.choice(moves_coords)
        mv = coords_to_move(r,c)
        moves.append(mv)
        b.apply_move_coords(r,c,player)
        player = -player
    return moves
