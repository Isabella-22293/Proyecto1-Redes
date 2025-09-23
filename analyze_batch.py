from pathlib import Path
import json, csv
from othello_engine import analyze_game
import matplotlib.pyplot as plt

GAMES_DIR = Path(__file__).parent / "games"
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

rows = []
for f in GAMES_DIR.glob("*.json"):
    data = json.loads(f.read_text(encoding="utf-8"))
    moves = data.get("moves", [])
    res = analyze_game(moves, max_depth=3)
    summary = res.get("summary", {})
    rows.append({
        "file": f.name,
        "moves": len(moves),
        "errors_count": summary.get("errors_count", 0),
        "first_error_index": summary.get("first_error_index", None)
    })

csv_path = REPORTS_DIR / "batch_summary.csv"
with csv_path.open("w", newline='', encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=["file","moves","errors_count","first_error_index"])
    writer.writeheader()
    writer.writerows(rows)

# Chart
files = [r["file"] for r in rows]
errors = [r["errors_count"] for r in rows]
plt.figure(figsize=(8,4))
plt.bar(range(len(files)), errors)
plt.xticks(range(len(files)), files, rotation=45, ha='right')
plt.ylabel("Errors count")
plt.title("Errores por partida (análisis automático)")
plt.tight_layout()
plt.savefig(str(REPORTS_DIR / "errors_per_game.png"))
print("Batch analysis saved:", csv_path)
