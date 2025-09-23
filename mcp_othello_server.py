from fastapi import FastAPI, Request, HTTPException
from pathlib import Path
import json
import uuid
from datetime import datetime
import logging

from othello_engine import analyze_game, board_after_moves, generate_random_game

# PNG generation
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_othello_server")

APP_ROOT = Path(__file__).parent.resolve()
GAMES_DIR = APP_ROOT / "games"
REPORTS_DIR = APP_ROOT / "reports"
for d in (GAMES_DIR, REPORTS_DIR):
    d.mkdir(exist_ok=True)

app = FastAPI(title="Othello MCP Server", version="0.1")

# store minimal in-memory map: game_id -> {moves, metadata, analysis}
GAMES = {}

def board_to_png_matrix(board_matrix, path: Path):
    fig, ax = plt.subplots(figsize=(4,4))
    # draw board squares
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(0,8); ax.set_ylim(8,0)
    # draw grid
    for r in range(8):
        for c in range(8):
            rect = plt.Rectangle((c, r), 1, 1, fill=True, color=(0.7,0.9,0.7))
            ax.add_patch(rect)
    # draw discs
    for r in range(8):
        for c in range(8):
            v = board_matrix[r][c]
            if v != 0:
                color = 'black' if v==1 else 'white'
                circ = plt.Circle((c + 0.5, r + 0.5), 0.35, color=color, ec='black')
                ax.add_patch(circ)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(str(path), dpi=150)
    plt.close(fig)

def make_jsonrpc_error(id_, code, message):
    return {"jsonrpc":"2.0", "id": id_, "error":{"code":code, "message":message}}

def make_jsonrpc_result(id_, result):
    return {"jsonrpc":"2.0", "id": id_, "result": result}

@app.post("/rpc")
async def rpc(request: Request):
    payload = await request.json()
    logger.info("RPC request: %s", payload.get("method"))
    if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
        raise HTTPException(status_code=400, detail="Invalid JSON-RPC envelope")
    method = payload.get("method")
    params = payload.get("params", {})
    id_ = payload.get("id")
    try:
        if method == "fetch_game":
            result = await rpc_fetch_game(params)
            return make_jsonrpc_result(id_, result)
        elif method == "load_game":
            result = await rpc_load_game(params)
            return make_jsonrpc_result(id_, result)
        elif method == "analyze_game":
            result = await rpc_analyze_game(params)
            return make_jsonrpc_result(id_, result)
        elif method == "simulate":
            result = await rpc_simulate(params)
            return make_jsonrpc_result(id_, result)
        elif method == "export_report":
            result = await rpc_export_report(params)
            return make_jsonrpc_result(id_, result)
        else:
            return make_jsonrpc_error(id_, -32601, f"Method {method} not found")
    except Exception as e:
        logger.exception("Error handling RPC")
        return make_jsonrpc_error(id_, -32000, f"Internal error: {str(e)}")

async def rpc_fetch_game(params):
    """
    params:
      source: 'local'|'random'
      file_path: if local
    """
    source = params.get("source", "random")
    if source == "local":
        fp = params.get("file_path")
        if not fp:
            raise Exception("file_path required for local source")
        p = Path(fp)
        if not p.exists():
            raise Exception(f"{fp} not found")
        text = p.read_text(encoding="utf-8")
        try:
            payload = json.loads(text)
            moves = payload.get("moves", [])
            metadata = payload.get("metadata", {})
        except Exception:
            # fallback: lines
            moves = [l.strip() for l in text.splitlines() if l.strip()]
            metadata = {}
    elif source == "random":
        moves = generate_random_game()
        metadata = {"generated": True}
    else:
        raise Exception(f"Source {source} not implemented in this server")

    gid = str(uuid.uuid4())
    GAMES[gid] = {"moves": moves, "metadata": metadata, "created": datetime.utcnow().isoformat()}
    (GAMES_DIR / f"{gid}.json").write_text(json.dumps({"moves":moves,"metadata":metadata}, indent=2), encoding="utf-8")
    return {"game_id": gid, "moves_count": len(moves), "source": source}

async def rpc_load_game(params):
    # alias
    return await rpc_fetch_game(params)

async def rpc_analyze_game(params):
    gid = params.get("game_id")
    moves = params.get("moves")
    max_depth = int(params.get("max_depth", 4))
    if not moves and gid:
        entry = GAMES.get(gid)
        if not entry:
            raise Exception("game_id not found")
        moves = entry["moves"]
    if not moves:
        raise Exception("moves or game_id required")
    result = analyze_game(moves, max_depth=max_depth)
    if gid:
        GAMES[gid]["analysis"] = result
    else:
        gid = str(uuid.uuid4())
        GAMES[gid] = {"moves": moves, "analysis": result, "metadata": {}, "created": datetime.utcnow().isoformat()}
    return {"game_id": gid, "analysis_summary": result.get("summary"), "analysis_length": len(result.get("analysis", []))}

async def rpc_simulate(params):
    gid = params.get("game_id")
    until = int(params.get("until_move", 0))
    max_depth = int(params.get("max_depth", 4))
    if not gid:
        raise Exception("game_id required")
    entry = GAMES.get(gid)
    if not entry:
        raise Exception("game_id not found")
    moves = entry["moves"]
    partial = moves[:until]
    # analyze partial position
    res = analyze_game(partial, max_depth=max_depth)
    # find suggested root move (engine_best for move_index == len(partial))
    # We compute best move on partial board:
    from othello_engine import Board, find_best_move
    b = Board()
    player = 1
    for m in partial:
        if m and str(m).strip().lower()!="pass":
            b.apply_move(m, player)
        player = -player
    best_move, pv, val = find_best_move(b, player, max_depth)
    return {"game_id": gid, "until_move": until, "suggested_move": best_move, "pv": pv, "raw_analysis": res}

async def rpc_export_report(params):
    gid = params.get("game_id")
    fmt = params.get("format", "both")
    path = params.get("path", str(REPORTS_DIR))
    if not gid:
        raise Exception("game_id required")
    entry = GAMES.get(gid)
    if not entry:
        raise Exception("game_id not found")
    analysis = entry.get("analysis") or analyze_game(entry["moves"])
    target_dir = Path(path)
    target_dir.mkdir(parents=True, exist_ok=True)
    base = target_dir / f"{gid}"
    json_path = base.with_suffix(".json")
    json_path.write_text(json.dumps({"game_id":gid, "moves": entry["moves"], "analysis": analysis}, indent=2), encoding="utf-8")
    # board PNG
    board = board_after_moves(entry["moves"])
    png_path = base.with_suffix(".png")
    board_to_png_matrix(board, png_path)
    html_path = base.with_suffix(".html")
    html = f"""<html><head><meta charset='utf-8'><title>Othello Analysis {gid}</title></head><body>
    <h1>Othello Analysis {gid}</h1>
    <p>Moves: {len(entry['moves'])}</p>
    <img src="{png_path.name}" alt="board"/><pre>{json.dumps(analysis, indent=2)}</pre>
    </body></html>"""
    html_path.write_text(html, encoding="utf-8")
    return {"game_id": gid, "json": str(json_path), "html": str(html_path), "png": str(png_path)}
