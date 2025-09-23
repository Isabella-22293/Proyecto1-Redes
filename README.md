# Othello Coach MCP

Este repo contiene un servidor MCP para analizar partidas de Othello.  
Provee:
- Servidor JSON-RPC (`/rpc`) con métodos: `load_game`, `fetch_game`, `analyze_game`, `simulate`, `export_report`.
- Motor Othello simple (`othello_engine.py`) con negamax + heurística.
- Generador de partidas de ejemplo, utilidades CLI y análisis por lote.
- Exportación de reportes JSON / HTML y PNG del tablero.

## Instalación rápida
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
