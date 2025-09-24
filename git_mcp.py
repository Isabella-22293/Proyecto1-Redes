from fastapi import FastAPI, Request
import uvicorn
import uuid

app = FastAPI()
repos = {}

@app.post("/rpc")
async def rpc(request: Request):
    req = await request.json()
    method = req.get("method")
    params = req.get("params", {})
    id_ = req.get("id", str(uuid.uuid4()))

    if method == "git.create_repo":
        name = params.get("name")
        repo_id = str(uuid.uuid4())
        repos[repo_id] = {"name": name}
        result = {"status": "ok", "repo_id": repo_id, "name": name}
    else:
        result = {"error": f"Método {method} no implementado"}

    return {"jsonrpc": "2.0", "id": id_, "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
