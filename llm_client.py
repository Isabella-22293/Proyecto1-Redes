import os, time, json
from typing import List, Dict
import requests
from config import LLM_PROVIDER, ANTHROPIC_API_KEY

class LLMClient:
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.api_key = ANTHROPIC_API_KEY
        self.model = os.getenv("LLM_MODEL", "claude-2")  # ajustar si usas Anthropic
        # conversation stored as list of {"role": "user"|"assistant"|"system", "content": "..."}
        self.reset_context()

    def reset_context(self, system_prompt: str = None):
        self.context = []
        if system_prompt:
            self.context.append({"role": "system", "content": system_prompt})

    def add_user_message(self, text: str):
        self.context.append({"role": "user", "content": text})

    def add_assistant_message(self, text: str):
        self.context.append({"role": "assistant", "content": text})

    def get_context_messages(self) -> List[Dict]:
        return self.context

    def trim_context(self, max_msgs: int):
        if len(self.context) > max_msgs:
            # keep system (if any) + last max_msgs-1
            sys_msgs = [m for m in self.context if m["role"] == "system"]
            others = [m for m in self.context if m["role"] != "system"]
            keep = sys_msgs + others[-(max_msgs - len(sys_msgs)):]
            self.context = keep

    def ask(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Añade el prompt a contexto, consulta al provider (o al stub) y devuelve respuesta.
        """
        self.add_user_message(prompt)
        if self.provider.lower() == "anthropic" and self.api_key:
            return self._ask_anthropic(prompt, max_tokens)
        else:
            return self._ask_stub(prompt)

    def _ask_stub(self, prompt: str) -> str:
        # respuesta simple: eco + ayuda sobre comandos MCP
        resp = f"(respuesta-STUB) He leído tu pregunta: {prompt}\n\nComandos útiles:\n" \
               "/load_local_game <ruta>  - cargar partida local en servidor Othello\n" \
               "/analyze <game_id>       - analizar partida\n" \
               "/simulate <game_id> <n>  - simular hasta n\n" \
               "Si quieres usar Anthropic, configura ANTHROPIC_API_KEY y LLM_PROVIDER=anthropic.\n"
        self.add_assistant_message(resp)
        return resp

    def _ask_anthropic(self, prompt: str, max_tokens: int) -> str:
        """
        Implementación HTTP básica para Anthropic. **Verifica** el endpoint y encabezados
        según la versión de la API que uses; algunos SDK exigen Authorization Bearer u otra cabecera.
        """
        # construir 'prompt' concatenando contexto (simple)
        messages = []
        for m in self.context:
            role = m["role"]
            content = m["content"]
            messages.append(f"{role.upper()}:\n{content}\n")
        full_prompt = "\n\n".join(messages)
        # La API de Anthropic históricamente usaba /v1/complete o endpoints similares.
        # Aquí hacemos un intento con el endpoint público:
        url = "https://api.anthropic.com/v1/complete"
        headers = {
            "x-api-key": self.api_key,        # si tu versión requiere Bearer, cámbialo
            "Content-Type": "application/json"
        }
        body = {
            "model": self.model,
            "prompt": full_prompt + "\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": 0.2,
        }
        r = requests.post(url, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        # la estructura de respuesta puede variar; aquí asumimos `completion` / `output` / `text`
        # intenta mapear según la respuesta real de tu cuenta
        if "completion" in data:
            text = data["completion"]
        elif "output" in data and isinstance(data["output"], list):
            # caso: salida en bloques
            text = " ".join([o.get("content", "") for o in data["output"]])
        else:
            text = data.get("text") or data.get("completion") or str(data)
        self.add_assistant_message(text)
        return text
