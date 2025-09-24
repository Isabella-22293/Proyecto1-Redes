from mcp_client import call_mcp
import json, time
import os

URL = "http://localhost:8080/rpc"

# --- 1) Cargar juego local ---
sample_file = "games/sample_game.json"
if not os.path.exists(sample_file):
    raise FileNotFoundError(f"No se encontró {sample_file}. Crea un juego de ejemplo allí.")

print("Loading local sample...")
res = call_mcp(URL, "load_game", {"source": "local", "file_path": sample_file})
print("load_game result:", json.dumps(res, indent=2))
gid = res["game_id"]

# Obtenemos la lista de movimientos si está disponible
moves = res.get("moves", [])

time.sleep(0.3)

# --- 2) Analizar el juego ---
print("\nAnalyzing...")
res2 = call_mcp(URL, "analyze_game", {
    "game_id": gid,
    "moves": moves,     # enviamos los movimientos jugados
    "max_depth": 4
})
print("analyze_game summary keys:", list(res2.keys()))
print(json.dumps(res2.get("analysis_summary", {}), indent=2)[:1000])

time.sleep(0.3)

# --- 3) Simular hasta cierto movimiento ---
print("\nSimulating until move 10...")
res3 = call_mcp(URL, "simulate", {
    "game_id": gid,
    "until_move": 10,
    "max_depth": 5
})
print(json.dumps(res3, indent=2))

time.sleep(0.3)

# --- 4) Exportar reporte ---
report_path = "reports"
os.makedirs(report_path, exist_ok=True)
print("\nExporting report to reports/")
res4 = call_mcp(URL, "export_report", {
    "game_id": gid,
    "format": "both",
    "path": report_path
})
print(json.dumps(res4, indent=2))
