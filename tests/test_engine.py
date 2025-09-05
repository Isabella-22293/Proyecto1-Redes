from engine.board import empty_board, legal_moves

def test_initial_moves():
    b = empty_board()
    # initial position has 4 legal moves for Black
    assert len(legal_moves(b,'B')) == 4
