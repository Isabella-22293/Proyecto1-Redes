from flask import Flask, request, jsonify
import uuid
from engine.board import empty_board, apply_moves_from_list, alg_from_coord
from engine.analyzer import analyze_game, suggest_move_from_moves
import os
from matplotlib import pyplot as plt

app = Flask(__name__)
GAMES = {}


@app.route('/load_game', methods=['POST'])
def load_game():
    data = request.json or {}
    moves = data.get('moves', [])
    gid = str(uuid.uuid4())
    GAMES[gid] = moves
    return jsonify({'status':'ok','game_id':gid,'moves_count':len(moves)})

@app.route('/analyze_game', methods=['POST'])
def analyze_game_endpoint():
    payload = request.json or {}
    moves = payload.get('moves') or []
    max_depth = int(payload.get('max_depth', 6))
    iterative = bool(payload.get('iterative', True))
    swing_t = float(payload.get('error_swing_threshold', 1.0))
    time_limit = float(payload.get('time_limit', 2.0))
    try:
        out = analyze_game(moves, max_depth=max_depth, iterative=iterative, swing_threshold=swing_t, time_limit_per_pos=time_limit)
        return jsonify({'status':'ok','result':out})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/suggest_move', methods=['POST'])
def suggest_move_endpoint():
    payload = request.json or {}
    moves = payload.get('moves', [])
    max_depth = int(payload.get('max_depth', 6))
    time_limit = float(payload.get('time_limit', 2.0))
    try:
        out = suggest_move_from_moves(moves, max_depth=max_depth, time_limit=time_limit)
        return jsonify({'status':'ok','result':out})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500


def board_to_png(board_matrix, out_path):
    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_xticks([])
    ax.set_yticks([])
    for r in range(8):
        for c in range(8):
            color = "#9dbf9e" if (r+c)%2==0 else "#7aa87a"
            rect = plt.Rectangle((c,7-r),1,1, facecolor=color)
            ax.add_patch(rect)
            val = board_matrix[r][c]
            if val == 1:
                ax.add_patch(plt.Circle((c+0.5,7-r+0.5),0.35, color="black"))
            elif val == -1:
                ax.add_patch(plt.Circle((c+0.5,7-r+0.5),0.35, color="white", ec="black"))
    ax.set_xlim(0,8)
    ax.set_ylim(0,8)
    plt.axis('off')
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close(fig)

@app.route('/mcp', methods=['POST'])
def mcp_rpc():
    data = request.get_json() or {}
    method = data.get("method")
    rpc_id = data.get("id", str(uuid.uuid4()))

    if method == "resources/list":
        result = ["load_game", "analyze_game", "suggest_move"]
    elif method == "tools/list":
        result = ["suggest_move", "analyze_game"]
    else:
        return jsonify({"jsonrpc": "2.0", "id": rpc_id, "error": f"Method {method} not found"}), 404

    return jsonify({"jsonrpc": "2.0", "id": rpc_id, "result": result})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
