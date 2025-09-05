import pytest
from engine.board import empty_board, legal_moves, apply_move, coord_from_alg, alg_from_coord, count_discs

def test_empty_board_has_start_position():
    b = empty_board()
    # Las fichas iniciales deben estar en (3,3)=W, (3,4)=B, (4,3)=B, (4,4)=W
    assert b[3][3] == 'W'
    assert b[3][4] == 'B'
    assert b[4][3] == 'B'
    assert b[4][4] == 'W'

def test_initial_moves_for_black():
    b = empty_board()
    moves = legal_moves(b, 'B')
    assert len(moves) == 4
    alg_moves = [alg_from_coord(m) for m in moves]
    assert set(alg_moves) == {"d3", "c4", "f5", "e6"}

def test_apply_move_and_count():
    b = empty_board()
    r, c = coord_from_alg("d3")
    ok = apply_move(b, r, c, 'B')
    assert ok
    counts = count_discs(b)
    # después de d3 por negras, deben haber 4 negras y 1 blanca
    assert counts['B'] == 4
    assert counts['W'] == 1
