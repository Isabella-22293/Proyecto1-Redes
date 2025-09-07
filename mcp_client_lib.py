import requests
import uuid

class MCPHttpClient:
    def __init__(self, url, timeout=10):
        self.url = url
        self.timeout = timeout

    def _payload(self, method, params=None):
        return {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {}
        }

    def call(self, method, params=None):
        payload = self._payload(method, params)
        r = requests.post(self.url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        resp = r.json()
        if "error" in resp and resp["error"] is not None:
            raise Exception(f"JSON-RPC error: {resp['error']}")
        return resp.get("result")

    def discover_resources(self):
        return self.call("resources/list")

    def list_tools(self):
        try:
            return self.call("tools/list")
        except Exception:
            return None
