from fastapi import FastAPI, Request
import uvicorn
import json
import uuid

app = FastAPI()

games = {}  # almacenar partidas en memoria

@app.post("/rpc")
async def rpc(request: Request):
    req = await request.json()
    method = req.get("method")
    params = req.get("params", {})
    id_ = req.get("id", str(uuid.uuid4()))

    if method == "load_game":
        source = params.get("source")
        file_path = params.get("file_path")
        # cargar juego desde archivo (simulado)
        game_id = str(uuid.uuid4())
        games[game_id] = {"moves_count": 0, "source": source}
        result = {"game_id": game_id, "moves_count": 0, "source": source}

    elif method == "analyze_game":
        game_id = params.get("game_id")
        result = {"analysis": f"Análisis simulado para {game_id}"}

    elif method == "simulate":
        game_id = params.get("game_id")
        until = params.get("until_move")
        result = {"simulation": f"Simulación hasta {until} jugadas para {game_id}"}

    elif method == "export_report":
        game_id = params.get("game_id")
        result = {"report": f"Reporte JSON/HTML para {game_id}"}

    else:
        result = {"error": f"Método {method} no implementado"}

    return {"jsonrpc": "2.0", "id": id_, "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
