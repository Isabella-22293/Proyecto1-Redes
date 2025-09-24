import requests
import json
import uuid
from typing import Any, Dict

def call_mcp(endpoint: str, method: str, params: Dict[str, Any] = None, timeout: int = 60):
    """
    Llama un servidor MCP/JSON-RPC.
    Devuelve dict con la respuesta JSON (o lanza excepción).
    """
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params or {}
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    resp = r.json()
    # JSON-RPC error?
    if "error" in resp:
        raise RuntimeError(f"MCP error: {resp['error']}")
    return resp.get("result")
