import os
import requests
from config import ANTHROPIC_API_KEY, CONTEXT_MAX_MESSAGES

class LLMClient:
    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1/complete"
        self.context_messages = []

    def reset_context(self, system_prompt=""):
        """Reinicia el contexto con un mensaje del sistema opcional"""
        self.context_messages = []
        if system_prompt:
            # Anthropic usa prefijo "system" como mensaje inicial
            self.context_messages.append({"role": "system", "content": system_prompt})

    def add_assistant_message(self, message):
        """Agrega un mensaje del asistente al contexto"""
        self.context_messages.append({"role": "assistant", "content": message})
        self.trim_context(CONTEXT_MAX_MESSAGES)

    def get_context_messages(self):
        """Devuelve los mensajes actuales en contexto"""
        return self.context_messages

    def trim_context(self, max_messages):
        """Mantiene solo los últimos max_messages en contexto"""
        self.context_messages = self.context_messages[-max_messages:]

    def ask(self, user_input, max_tokens=300):
        """Envía una pregunta al LLM y devuelve la respuesta"""
        self.context_messages.append({"role": "user", "content": user_input})
        # Construye el prompt con los prefijos de Anthropic
        # Claude espera: Human: ... \nAssistant: ...
        prompt_parts = []
        for m in self.context_messages:
            if m["role"] == "system":
                prompt_parts.append(f"{m['content']}\n")
            elif m["role"] == "user":
                prompt_parts.append(f"Human: {m['content']}\n")
            elif m["role"] == "assistant":
                prompt_parts.append(f"Assistant: {m['content']}\n")
        # Indicar que Anthropic debe responder como Assistant
        prompt_parts.append("Assistant:")

        prompt = "".join(prompt_parts)

        payload = {
            "model": "claude-2",
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": 0.7,
            "stop_sequences": ["\nHuman:"]
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Anthropic-Version": "2023-06-01"
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            completion = data.get("completion", "").strip()
            # Guarda la respuesta en contexto
            self.context_messages.append({"role": "assistant", "content": completion})
            self.trim_context(CONTEXT_MAX_MESSAGES)
            return completion
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM request failed: {str(e)}")
        except ValueError:
            raise Exception(f"LLM response could not be decoded: {response.text}")
