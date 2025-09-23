from pathlib import Path
from othello_engine import generate_random_game
import json

GAMES_DIR = Path(__file__).parent / "games"
GAMES_DIR.mkdir(exist_ok=True)
moves = generate_random_game()
out = {"moves": moves, "metadata": {"generated_by":"generate_sample_game.py"}}
p = GAMES_DIR / "sample_game.json"
p.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("Saved sample game to", p)
