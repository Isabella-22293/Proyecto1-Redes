from fastapi import FastAPI, Request
import uvicorn
import json
import os
import uuid

app = FastAPI()

@app.post("/rpc")
async def rpc(request: Request):
    req = await request.json()
    method = req.get("method")
    params = req.get("params", {})
    id_ = req.get("id", str(uuid.uuid4()))

    try:
        if method == "filesystem.write_file":
            path = params.get("path")
            content = params.get("content", "")
            # Crear carpeta solo si existe
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            result = {"status": "ok", "path": path}

        elif method == "filesystem.read_file":
            path = params.get("path")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                result = {"status": "ok", "content": content}
            else:
                result = {"status": "error", "message": "Archivo no encontrado"}

        else:
            result = {"error": f"Método {method} no implementado"}

    except Exception as e:
        result = {"status": "error", "message": str(e)}

    return {"jsonrpc": "2.0", "id": id_, "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
