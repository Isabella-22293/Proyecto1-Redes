from chatbot_host import safe_call_mcp, OTHELLO_MCP_ENDPOINT

res = safe_call_mcp(
    OTHELLO_MCP_ENDPOINT,
    'load_game',
    {'source': 'local', 'file_path': 'games/sample_game.json'}
)

with open('last_game_id.txt', 'w') as f:
    f.write(res.get('game_id', ''))

print('Game ID extraído:', res.get('game_id', ''))
