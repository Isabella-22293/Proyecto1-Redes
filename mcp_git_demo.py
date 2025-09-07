from mcp_client_lib import MCPHttpClient
import os, json

URL = os.environ.get("GIT_MCP_URL", "http://127.0.0.1:5001/mcp")

def main():
    client = MCPHttpClient(URL)
    resources = client.discover_resources()
    print("resources:", json.dumps(resources, indent=2))
    try:
        tools = client.call("tools/list")
        print("tools:", json.dumps(tools, indent=2))
    except Exception as e:
        print("tools/list no disponible:", e)
        return
    example_tool_id = "git/create_repo"
    params = {"name": "demo-repo", "description": "Repo creado por MCP demo"}
    try:
        resp = client.call("tools/call", {"tool_id": example_tool_id, "params": params})
        print("create_repo resp:", resp)
    except Exception as e:
        print("tools/call falló (revisa tool_id):", e)

if __name__ == "__main__":
    main()
