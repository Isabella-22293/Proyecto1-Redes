from othello_engine_adapter import OthelloEngineInteractive
from othello_ui_interactive import OthelloUIInteractive

def main():
    engine=OthelloEngineInteractive()
    ui=OthelloUIInteractive(engine)
    print("\n¡Bienvenido a Othello Interactive!")
    print("Usa letras a-h y números 1-8 para mover, 'pass' para pasar, 'q' para salir.\n")
    ui.run_game_interactive()
    print("\n¡Juego terminado!")
    counts=engine.board.counts()
    print(f"Puntuación final: B={counts['black']}, W={counts['white']}")
    if counts['black']>counts['white']:
        print("¡Ganó Black!")
    elif counts['white']>counts['black']:
        print("¡Ganó White!")
    else:
        print("Empate!")

if __name__=="__main__":
    main()
