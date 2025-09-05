# engine/evaluate.py
from .board import legal_moves, count_discs, opponent

POS_WEIGHTS = [
 [100, -20, 10, 5, 5, 10, -20,100],
 [-20, -50, -2, -2, -2, -2, -50,-20],
 [10, -2, -1, -1, -1, -1, -2, 10],
 [5, -2, -1, -1, -1, -1, -2, 5],
 [5, -2, -1, -1, -1, -1, -2, 5],
 [10, -2, -1, -1, -1, -1, -2, 10],
 [-20, -50, -2, -2, -2, -2, -50,-20],
 [100, -20, 10, 5, 5, 10, -20,100]
]

def evaluate(board, player):
    opp = opponent(player)
    discs = count_discs(board)
    material = discs[player] - discs[opp]
    pos = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                pos += POS_WEIGHTS[r][c]
            elif board[r][c] == opp:
                pos -= POS_WEIGHTS[r][c]
    mob = len(legal_moves(board,player)) - len(legal_moves(board,opp))
    return 0.1*material + 0.01*mob + 0.001*pos
