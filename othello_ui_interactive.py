from othello_engine_adapter import OthelloEngineInteractive, move_to_coords, BLACK, WHITE, coords_to_move

class OthelloUIInteractive:
    def __init__(self, engine:OthelloEngineInteractive):
        self.engine=engine
        self.last_move=None

    def print_board(self):
        legal_coords = [move_to_coords(mv) for mv in self.engine.get_legal_moves()]
        print("\n  A B C D E F G H")
        for r in range(8):
            row_str=str(r+1)+" "
            for c in range(8):
                cell=self.engine.board.b[r][c]
                pos=(r,c)
                # Resaltar última jugada
                if self.last_move==pos:
                    if cell==BLACK: row_str+="*B* "
                    elif cell==WHITE: row_str+="*W* "
                    else: row_str+=".*. "
                # Resaltar jugadas legales
                elif pos in legal_coords:
                    row_str+="+ "
                else:
                    if cell==BLACK: row_str+="B "
                    elif cell==WHITE: row_str+="W "
                    else: row_str+=". "
            print(row_str)

    def print_pv(self,pv_moves):
        if not pv_moves: return
        print("PV:", " -> ".join(pv_moves))

    def run_game_interactive(self):
        while not self.engine.board.is_terminal():
            self.print_board()
            pv=self.engine.get_pv(max_depth=3)
            self.print_pv(pv)
            player_str="B" if self.engine.current_color==BLACK else "W"
            print(f"Turno: {player_str}")
            move=None
            while True:
                move=input("Ingresa jugada (ej: d3) o 'pass': ").strip().lower()
                if move=="q": return
                # Validar jugada
                if move=="pass" or move in self.engine.get_legal_moves():
                    ok=self.engine.apply_move(move)
                    if ok:
                        if move!="pass":
                            self.last_move=move_to_coords(move)
                        break
                print("Movimiento inválido, intenta de nuevo.")
            _=input("Presiona Enter para siguiente turno o 'q' para salir: ")
