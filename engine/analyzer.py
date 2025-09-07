from .board import empty_board, apply_moves_from_list, alg_from_coord, clone_board, apply_move, count_discs
from .search import search_best
from .evaluate import evaluate

def analyze_game(moves, max_depth=6, iterative=True, swing_threshold=1.0, time_limit_per_pos=2.0):
    results = []
    board = empty_board()
    current = 'B'
    first_error = None
    for ply, mv in enumerate(moves, start=1):
        try:
            best = search_best(board, current, max_depth=max_depth, time_limit=time_limit_per_pos if iterative else None)
        except Exception:
            best = {'value': evaluate(board,current), 'pv': [], 'depth':0, 'nodes':0, 'time':0}
        best_move = best['pv'][0] if best['pv'] else None
        eval_before = evaluate(board, current)
        # apply real move
        temp = clone_board(board)
        if mv == 'pass':
            real_move = None
        else:
            real_move = (int(mv[1])-1, ord(mv[0].lower())-ord('a'))
        if real_move:
            applied = apply_move(temp, real_move[0], real_move[1], current)
            eval_after = evaluate(temp, current) if applied else evaluate(temp, current)
        else:
            eval_after = evaluate(temp, current)
        temp2 = clone_board(board)
        if best_move:
            apply_move(temp2, best_move[0], best_move[1], current)
            best_after_eval = evaluate(temp2, current)
        else:
            best_after_eval = eval_before
        swing = abs((best_after_eval if best_after_eval is not None else eval_before) - (eval_after if eval_after is not None else eval_before))
        move_is_best = (best_move == real_move)
        res = {
            'ply': ply,
            'player': current,
            'move': mv,
            'engine_best': alg_from_coord(best_move) if best_move else None,
            'move_is_best': move_is_best,
            'eval_before': eval_before,
            'eval_after_move': eval_after,
            'eval_best_after': best_after_eval,
            'swing': swing,
            'pv': [alg_from_coord(rc) for rc in best['pv']] if best.get('pv') else [],
            'depth_used': best.get('depth', 0),
            'nodes': best.get('nodes', 0),
            'time': best.get('time', 0)
        }
        results.append(res)
        if (not first_error) and (not move_is_best) and (swing > swing_threshold):
            first_error = {
                'ply': ply,
                'move': mv,
                'player': current,
                'swing': swing,
                'engine_best': alg_from_coord(best_move) if best_move else None,
                'pv': [alg_from_coord(rc) for rc in best['pv']] if best.get('pv') else []
            }
        if real_move:
            apply_move(board, real_move[0], real_move[1], current)
        current = 'W' if current=='B' else 'B'
    final_eval = evaluate(board, 'B')
    summary = {'final_eval': final_eval, 'discs': count_discs(board)}
    return {'analysis': results, 'first_error': first_error, 'summary': summary}

def suggest_move_from_moves(moves, max_depth=6, time_limit=None):
    b, current = apply_moves_from_list(moves)
    out = search_best(b, current, max_depth=max_depth, time_limit=time_limit)
    best_move = out['pv'][0] if out['pv'] else None
    return {
        'best_move': alg_from_coord(best_move) if best_move else None,
        'best_eval': out['value'],
        'pv': [alg_from_coord(rc) for rc in out['pv']],
        'depth': out['depth'],
        'nodes': out['nodes'],
        'time': out['time']
    }
