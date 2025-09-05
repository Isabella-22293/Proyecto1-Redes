# engine/search.py
import time
from .board import legal_moves, clone_board, apply_move, opponent
from .evaluate import evaluate

class SearchStats:
    def __init__(self):
        self.nodes = 0
        self.start_time = time.time()
        self.time_limit = None

    def timeout(self):
        return self.time_limit is not None and (time.time() - self.start_time) > self.time_limit

def negamax(board, player, depth, alpha, beta, stats):
    stats.nodes += 1
    if stats.timeout():
        raise TimeoutError()
    moves = legal_moves(board, player)
    if depth == 0 or not moves:
        return evaluate(board, player), []
    best_val = -float('inf')
    best_line = []
    for (r,c) in moves:
        nb = clone_board(board)
        apply_move(nb, r, c, player)
        val, line = negamax(nb, opponent(player), depth-1, -beta, -alpha, stats)
        val = -val
        if val > best_val:
            best_val = val
            best_line = [(r,c)] + line
        alpha = max(alpha, val)
        if alpha >= beta:
            break
    return best_val, best_line

def search_best(board, player, max_depth=6, time_limit=None):
    stats = SearchStats()
    stats.time_limit = time_limit
    best_val = None
    best_line = []
    depth_reached = 0
    try:
        for d in range(1, max_depth+1):
            val, line = negamax(board, player, d, -1e9, 1e9, stats)
            best_val = val
            best_line = line
            depth_reached = d
    except TimeoutError:
        pass
    return {
        'value': best_val if best_val is not None else evaluate(board, player),
        'pv': [(r,c) for (r,c) in best_line],
        'depth': depth_reached,
        'nodes': stats.nodes,
        'time': time.time() - stats.start_time
    }
