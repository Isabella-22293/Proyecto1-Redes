from flask import Flask, request, jsonify
import uuid
from engine.board import empty_board, apply_moves_from_list, alg_from_coord
from engine.analyzer import analyze_game, suggest_move_from_moves

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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
