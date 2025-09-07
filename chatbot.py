import os
import json
import time
import requests
from datetime import datetime
from mcp_client_lib import MCPHttpClient

LOG_FILE = os.environ.get("CHATBOT_LOG", "logs/session.log")
OTHELLO_MCP_URL = os.environ.get("OTHELLO_MCP_URL", "http://127.0.0.1:5001")  
FILESYSTEM_MCP_URL = os.environ.get("FILESYSTEM_MCP_URL","http://127.0.0.1:5001/mcp") 
GIT_MCP_URL = os.environ.get("GIT_MCP_URL")

class LLMClient:
    def __init__(self):
        self.mode = "mock"
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        if self.openai_key:
            try:
                import openai
                openai.api_key = self.openai_key
                self.openai = openai
                self.mode = "openai"
            except Exception:
                self.mode = "mock"

    def chat(self, messages):
        # messages: list of {"role": "user"/"assistant", "content": "..."}
        if self.mode == "openai":
            resp = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":m["role"], "content": m["content"]} for m in messages]
            )
            return resp.choices[0].message.content
        last = messages[-1]["content"]
        return f"[MOCK LLM] Recibido: {last}"

#logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(entry: dict):
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

#helpers para othello MCP
def post_othello(path, payload):
    url = OTHELLO_MCP_URL.rstrip("/") + path
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()

#command-line chatbot
def repl():
    llm = LLMClient()
    convo = [] 
    print("Chatbot MCP — escribe /help para comandos. (Ctrl+C para salir)\n")
    while True:
        try:
            text = input("TÚ> ").strip()
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        if not text:
            continue
        if text.startswith("/"):
            parts = text.split(" ", 2)
            cmd = parts[0].lower()
            if cmd == "/help":
                print("""Comandos útiles:
                       /help
                        /exit
                        /history                - mostrar historial (breve)
                        /load_local <path>      - carga archivo de partida local y lo sube al MCP (POST /load_game)
                        /analyze <game_id>      - pide análisis al servidor Othello MCP (POST /analyze_game)
                        /suggest <game_id>      - solicita sugerencia de jugada (POST /suggest_move)
                        /mcp_list <url>         - lista recursos en servidor MCP (usa FILESYSTEM_MCP_URL si no se pasa url)
                        /mcp_fs_create <path> <content> - crea archivo via Filesystem MCP demo
                        """)
                continue
            if cmd == "/exit":
                print("Adiós.")
                break
            if cmd == "/history":
                for i,m in enumerate(convo[-10:], start=1):
                    print(i, m["role"], ":", m["content"][:200])
                continue
            if cmd == "/load_local":
                if len(parts) < 2:
                    print("Uso: /load_local path/to/game.json")
                    continue
                path = parts[1]
                if not os.path.exists(path):
                    print("Archivo no encontrado:", path)
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                try:
                    resp = post_othello("/load_game", data)
                    print("Respuesta /load_game:", resp)
                    log({"type":"mcp_othello","action":"load_game","request":data,"response":resp})
                except Exception as e:
                    print("Error enviando a othello_mcp:", e)
                continue
            if cmd == "/analyze":
                if len(parts) < 2:
                    print("Uso: /analyze <game_id>")
                    continue
                gid = parts[1]
                try:
                    resp = post_othello("/analyze_game", {"game_id": gid})
                    print("Análisis:", json.dumps(resp, indent=2, ensure_ascii=False))
                    log({"type":"mcp_othello","action":"analyze_game","game_id":gid,"response":resp})
                except Exception as e:
                    print("Error:", e)
                continue
            if cmd == "/suggest":
                if len(parts) < 2:
                    print("Uso: /suggest <game_id>")
                    continue
                gid = parts[1]
                try:
                    resp = post_othello("/suggest_move", {"game_id": gid})
                    print("Sugerencia:", resp)
                    log({"type":"mcp_othello","action":"suggest_move","game_id":gid,"response":resp})
                except Exception as e:
                    print("Error:", e)
                continue
            if cmd == "/mcp_list":
                url = parts[1] if len(parts) > 1 else FILESYSTEM_MCP_URL
                if not url:
                    print("Define FILESYSTEM_MCP_URL o usa /mcp_list <url>")
                    continue
                try:
                    client = MCPHttpClient(url)
                    resources = client.discover_resources()
                    print("resources/list ->", json.dumps(resources, indent=2, ensure_ascii=False))
                    log({"type":"mcp","action":"resources/list","url":url,"response":resources})
                except Exception as e:
                    print("Error discovery:", e)
                continue
            if cmd == "/mcp_fs_create":
                if len(parts) < 3:
                    print("Uso: /mcp_fs_create <path> <content>")
                    continue
                url = FILESYSTEM_MCP_URL
                if not url:
                    print("Define FILESYSTEM_MCP_URL en el entorno.")
                    continue
                filepath = parts[1]
                content = parts[2]
                client = MCPHttpClient(url)
                try:
                    res = client.discover_resources()
                    print("resources:", res)
                    tool_id = "filesystem/write"
                    params = {"path": filepath, "content": content}
                    try:
                        result = client.call("tools/call", {"tool_id": tool_id, "params": params})
                        print("tools/call result:", result)
                        log({"type":"mcp","action":"tools/call","tool_id":tool_id,"params":params,"result":result})
                    except Exception as e:
                        print("tools/call falló, inténtalo manualmente. Error:", e)
                except Exception as e:
                    print("Error discovering:", e)
                continue

        convo.append({"role":"user","content": text})
        context = convo[-8*2:] 
        try:
            answer = llm.chat(context)
        except Exception as e:
            answer = f"[LLM error] {e}"
        print("LLM>", answer)
        convo.append({"role":"assistant","content": answer})
        log({"type":"llm","request": context, "response": answer})

if __name__ == "__main__":
    repl()
