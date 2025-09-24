@echo off
setlocal enabledelayedexpansion

echo === Iniciando smoke test MCP (Windows) ===

REM Levantar servidor Othello en segundo plano
start "" python -m uvicorn mcp_othello_server:app --port 8080
echo Esperando 5 segundos a que el servidor inicie...
timeout /t 5 /nobreak >nul

REM Cargar partida de ejemplo y capturar game_id
for /f "tokens=*" %%i in ('python -c "from chatbot_host import safe_call_mcp, OTHELLO_MCP_ENDPOINT; import json; res=safe_call_mcp(OTHELLO_MCP_ENDPOINT,'load_game',{'source':'local','file_path':'games/sample_game.json'}); print(res['game_id'])"') do set GAME_ID=%%i

if not defined GAME_ID (
    echo No se pudo obtener game_id, abortando.
    exit /b 1
)

echo Game ID extraído: %GAME_ID%

REM Analizar partida
python -c "from chatbot_host import safe_call_mcp, OTHELLO_MCP_ENDPOINT, json; res=safe_call_mcp(OTHELLO_MCP_ENDPOINT,'analyze_game',{'game_id':'%GAME_ID%','max_depth':2}); print(json.dumps(res, indent=2))"
echo Analisis completado.

REM Exportar reporte
python -c "from chatbot_host import safe_call_mcp, OTHELLO_MCP_ENDPOINT, json; res=safe_call_mcp(OTHELLO_MCP_ENDPOINT,'export_report',{'game_id':'%GAME_ID%','format':'both'}); print(json.dumps(res, indent=2))"
echo Export completo.

echo === Smoke test finalizado ===
pause
