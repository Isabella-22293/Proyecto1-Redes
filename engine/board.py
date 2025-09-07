DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def empty_board():
    b = [['.' for _ in range(8)] for _ in range(8)]
    b[3][3]='W'; b[3][4]='B'; b[4][3]='B'; b[4][4]='W'
    return b

def clone_board(b):
    return [row[:] for row in b]

def in_bounds(r,c):
    return 0<=r<8 and 0<=c<8

def opponent(player):
    return 'W' if player=='B' else 'B'

def coord_from_alg(s):
    if not isinstance(s, str) or len(s) < 2:
        raise ValueError('Invalid algebraic: '+str(s))
    c = ord(s[0].lower()) - ord('a')
    r = int(s[1]) - 1
    return (r,c)

def alg_from_coord(rc):
    if not rc:
        return None
    r,c = rc
    return chr(ord('a')+c)+str(r+1)

def would_flip(board, r, c, player):
    opp = opponent(player)
    for dr,dc in DIRECTIONS:
        rr,cc = r+dr, c+dc
        found_opp = False
        while in_bounds(rr,cc) and board[rr][cc] == opp:
            found_opp = True
            rr += dr; cc += dc
        if found_opp and in_bounds(rr,cc) and board[rr][cc] == player:
            return True
    return False

def legal_moves(board, player):
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c] != '.': continue
            if would_flip(board, r, c, player):
                moves.append((r,c))
    return moves

def apply_move(board, r, c, player):
    if not in_bounds(r,c) or board[r][c] != '.':
        return False
    flips = []
    opp = opponent(player)
    for dr,dc in DIRECTIONS:
        rr,cc = r+dr, c+dc
        path = []
        while in_bounds(rr,cc) and board[rr][cc] == opp:
            path.append((rr,cc)); rr += dr; cc += dc
        if path and in_bounds(rr,cc) and board[rr][cc] == player:
            flips.extend(path)
    if not flips:
        return False
    board[r][c] = player
    for (rr,cc) in flips:
        board[rr][cc] = player
    return True

def apply_moves_from_list(moves, board=None):
    if board is None:
        board = empty_board()
    b = clone_board(board)
    current = 'B'
    for s in moves:
        if isinstance(s, str) and s=='pass':
            current = opponent(current)
            continue
        if isinstance(s, str):
            r,c = coord_from_alg(s)
        else:
            r,c = s
        ok = apply_move(b, r, c, current)
        if not ok:
            raise ValueError(f"Invalid move {s} for player {current}")
        current = opponent(current)
    return b, current

def count_discs(board):
    b = sum(row.count('B') for row in board)
    w = sum(row.count('W') for row in board)
    return {'B':b,'W':w}
