import os, sys, time, json
from config import OTHELLO_MCP_ENDPOINT, FILESYSTEM_MCP_ENDPOINT, GIT_MCP_ENDPOINT, LOG_PATH, CONTEXT_MAX_MESSAGES
from llm_client import LLMClient
from mcp_client import call_mcp
from pathlib import Path

LOG_PATH = Path(LOG_PATH)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_entry(entry: dict):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

def pretty_print_json(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

def safe_call_mcp(endpoint, method, params=None):
    log_entry({"type":"mcp_request", "endpoint": endpoint, "method": method, "params": params})
    try:
        res = call_mcp(endpoint, method, params or {})
        log_entry({"type":"mcp_response", "endpoint": endpoint, "method": method, "result": res})
        return res
    except Exception as e:
        log_entry({"type":"mcp_error", "endpoint": endpoint, "method": method, "error": str(e)})
        raise

def interactive_loop():
    llm = LLMClient()
    system_prompt = "Eres un asistente que puede llamar servidores MCP (Filesystem, Git, Othello). Responde claramente. Usa comandos del anfitrión si el usuario lo pide."
    llm.reset_context(system_prompt=system_prompt)

    print("=== MCP Chatbot anfitrión (consola) ===")
    print("Escribe preguntas o usa comandos. Comandos disponibles: ")
    print("/help, /reset, /context, /ask <texto>")
    print("/load_local_game <ruta>  -> carga partida en servidor Othello local")
    print("/analyze <game_id>       -> analiza la partida con el servidor Othello")
    print("/simulate <game_id> <n>  -> simula hasta n jugadas")
    print("/export <game_id>        -> exporta reporte (json/html/png)")
    print("/git_create_repo <name>  -> intenta crear repo usando endpoint GIT_MCP_ENDPOINT")
    print("/fs_write <path> <text>  -> intenta escribir archivo usando FILESYSTEM_MCP_ENDPOINT")
    print("/exit")
    print("--------------------------------------------------")

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo.")
            break
        if not line:
            continue
        log_entry({"type":"user_input", "text": line})
        if line.startswith("/"):
            parts = line.split(" ", 2)
            cmd = parts[0].lower()
            try:
                if cmd == "/help":
                    print("Comandos: /help, /reset, /context, /ask, /load_local_game, /analyze, /simulate, /export, /git_create_repo, /fs_write, /exit")
                elif cmd == "/reset":
                    llm.reset_context(system_prompt=system_prompt)
                    print("Contexto reiniciado.")
                elif cmd == "/context":
                    pretty_print_json(llm.get_context_messages())
                elif cmd == "/ask":
                    if len(parts) < 2:
                        print("Sintaxis: /ask <pregunta>")
                        continue
                    q = parts[1]
                    resp = llm.ask(q)
                    print("LLM:", resp)
                    log_entry({"type":"llm_response", "text": resp})
                    # trim context to keep tokens small
                    llm.trim_context(CONTEXT_MAX_MESSAGES)
                elif cmd == "/load_local_game":
                    if len(parts) < 2:
                        print("Sintaxis: /load_local_game <ruta>")
                        continue
                    path = parts[1]
                    res = safe_call_mcp(OTHELLO_MCP_ENDPOINT, "load_game", {"source":"local", "file_path": path})
                    print("Resultado load_game:")
                    pretty_print_json(res)
                    # agrega un mensaje al contexto para referencia
                    llm.add_assistant_message(f"Cargada partida con id {res.get('game_id')}, movimientos: {res.get('moves_count')}")
                elif cmd == "/analyze":
                    if len(parts) < 2:
                        print("Sintaxis: /analyze <game_id>")
                        continue
                    gid = parts[1]
                    res = safe_call_mcp(OTHELLO_MCP_ENDPOINT, "analyze_game", {"game_id": gid, "max_depth": 4})
                    print("Análisis:")
                    pretty_print_json(res)
                elif cmd == "/simulate":
                    args = line.split()
                    if len(args) < 3:
                        print("Sintaxis: /simulate <game_id> <until>")
                        continue
                    gid = args[1]; until = int(args[2])
                    res = safe_call_mcp(OTHELLO_MCP_ENDPOINT, "simulate", {"game_id": gid, "until_move": until, "max_depth": 4})
                    print("Simulación:")
                    pretty_print_json(res)
                elif cmd == "/export":
                    if len(parts) < 2:
                        print("Sintaxis: /export <game_id>")
                        continue
                    gid = parts[1]
                    res = safe_call_mcp(OTHELLO_MCP_ENDPOINT, "export_report", {"game_id": gid, "format": "both"})
                    print("Export result:")
                    pretty_print_json(res)
                elif cmd == "/git_create_repo":
                    if not GIT_MCP_ENDPOINT:
                        print("GIT_MCP_ENDPOINT no configurado en config.py / env.")
                        continue
                    if len(parts) < 2:
                        print("Sintaxis: /git_create_repo <nombre>")
                        continue
                    name = parts[1]
                    res = safe_call_mcp(GIT_MCP_ENDPOINT, "git.create_repo", {"name": name})
                    print("git.create_repo result:")
                    pretty_print_json(res)
                elif cmd == "/fs_write":
                    if not FILESYSTEM_MCP_ENDPOINT:
                        print("FILESYSTEM_MCP_ENDPOINT no configurado en config.py / env.")
                        continue
                    if len(parts) < 3:
                        print("Sintaxis: /fs_write <ruta> <texto>")
                        continue
                    path = parts[1]; text = parts[2]
                    res = safe_call_mcp(FILESYSTEM_MCP_ENDPOINT, "filesystem.write_file", {"path": path, "content": text})
                    print("filesystem.write_file result:")
                    pretty_print_json(res)
                elif cmd == "/exit":
                    print("Adiós.")
                    break
                else:
                    print("Comando desconocido. Usa /help")
            except Exception as e:
                print("Error al ejecutar comando:", e)
        else:
            # mensaje libre -> preguntar LLM
            resp = llm.ask(line)
            print("LLM:", resp)
            log_entry({"type":"llm_response", "text": resp})

if __name__ == "__main__":
    interactive_loop()
