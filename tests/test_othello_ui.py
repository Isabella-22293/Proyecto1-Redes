import pytest
from othello_engine import Board, BLACK
from othello_ui_interactive import OthelloUIInteractive
from othello_engine_adapter import OthelloEngineInteractive

def test_ui_initialization():
    engine = OthelloEngineInteractive()
    ui = OthelloUIInteractive(engine)
    assert ui.engine is engine
    # prueba que el tablero inicial tiene 8 filas
    matrix = engine.board.to_matrix()
    assert len(matrix) == 8
    assert all(len(row) == 8 for row in matrix)
