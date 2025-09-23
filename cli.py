import argparse
import requests
import json

URL = "http://localhost:8080/rpc"

def rpc(method, params=None, id_=1):
    payload = {"jsonrpc":"2.0", "id": id_, "method": method, "params": params or {}}
    r = requests.post(URL, json=payload)
    try:
        return r.json()
    except Exception:
        print("Respuesta no-JSON:", r.text)
        return None

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("generate_sample")
    p = sub.add_parser("load")
    p.add_argument("--file", required=True)
    p = sub.add_parser("analyze")
    p.add_argument("--game_id", required=True)
    p = sub.add_parser("simulate")
    p.add_argument("--game_id", required=True)
    p.add_argument("--until", type=int, default=10)
    p = sub.add_parser("export")
    p.add_argument("--game_id", required=True)
    args = parser.parse_args()
    if args.cmd == "generate_sample":
        print("Use generate_sample_game.py to create a local sample, then load it.")
    elif args.cmd == "load":
        res = rpc("load_game", {"source":"local", "file_path": args.file})
        print(json.dumps(res, indent=2))
    elif args.cmd == "analyze":
        res = rpc("analyze_game", {"game_id": args.game_id, "max_depth":4})
        print(json.dumps(res, indent=2))
    elif args.cmd == "simulate":
        res = rpc("simulate", {"game_id": args.game_id, "until_move": args.until, "max_depth":4})
        print(json.dumps(res, indent=2))
    elif args.cmd == "export":
        res = rpc("export_report", {"game_id": args.game_id, "format":"both"})
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
