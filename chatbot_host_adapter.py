import json
from pathlib import Path
from chatbot_host import safe_call_mcp, interactive_loop

class ChatbotHost:
    def __init__(self, log_file="chat.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.fs_storage = {}  # simula filesystem para tests

    def log_entry(self, entry: dict):
        entry["ts"] = "2025-09-23T00:00:00Z"  # fijo para test
        with open(self.log_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def handle_command(self, command: str):
        """Ejecuta un comando simulado sin LLM ni MCP real"""
        if command.startswith("/fs write"):
            parts = command.split(" ", 3)
            path, text = parts[2], parts[3]
            self.fs_storage[path] = text
            return f"Wrote {path}"
        elif command.startswith("/fs read"):
            parts = command.split(" ", 2)
            path = parts[2]
            return self.fs_storage.get(path, "")
        elif command.startswith("/fs list"):
            return list(self.fs_storage.keys())
        elif command.startswith("/ask"):
            # stub de respuesta LLM
            return "Respuesta simulada"
        else:
            return "Comando desconocido"
