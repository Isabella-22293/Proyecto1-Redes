from mcp_client_lib import MCPHttpClient
import os, json

URL = os.environ.get("FILESYSTEM_MCP_URL", "http://127.0.0.1:5001/mcp")

def main():
    client = MCPHttpClient(URL)
    print("Discovering resources...")
    resources = client.discover_resources()
    print(json.dumps(resources, indent=2, ensure_ascii=False))
    print("\nIntentando un tools/list (si está disponible)...")
    try:
        tools = client.call("tools/list")
        print(json.dumps(tools, indent=2, ensure_ascii=False))
    except Exception as e:
        print("tools/list no disponible o falló:", e)

if __name__ == "__main__":
    main()
