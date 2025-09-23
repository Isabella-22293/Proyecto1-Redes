#!/usr/bin/env bash
set -e
URL="http://localhost:8080/rpc"

echo "1) Generate sample (locally):"
python3 generate_sample_game.py

echo "2) Load sample:"
curl -sS -X POST $URL -H "Content-Type: application/json" -d '{
  "jsonrpc":"2.0",
  "id":1,
  "method":"load_game",
  "params": {"source":"local", "file_path":"games/sample_game.json"}
}' | jq

# (sustituye <GAME_ID> por el id que obtengas en el resultado del anterior)
