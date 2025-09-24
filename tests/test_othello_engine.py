import pytest
from othello_engine import Board, BLACK, WHITE, move_to_coords, coords_to_move, find_best_move

def test_move_conversion():
    assert move_to_coords("d3") == (2,3)
    assert move_to_coords("a1") == (0,0)
    assert coords_to_move(2,3) == "d3"
    assert coords_to_move(0,0) == "a1"

def test_initial_board():
    b = Board()
    counts = b.counts()
    assert counts["black"] == 2
    assert counts["white"] == 2
    moves_black = b.legal_moves(BLACK)
    moves_white = b.legal_moves(WHITE)
    assert len(moves_black) > 0
    assert len(moves_white) > 0

def test_apply_move():
    b = Board()
    move = b.legal_moves(BLACK)[0]
    assert b.apply_move(move, BLACK)
    # después de aplicar, el movimiento ya no debe estar disponible
    assert move not in b.legal_moves(BLACK)

def test_find_best_move_returns_valid():
    b = Board()
    move, pv, val = find_best_move(b, BLACK, max_depth=2)
    assert move in b.legal_moves(BLACK) or move is None
    assert isinstance(pv, list)
    assert isinstance(val, (int,float))
