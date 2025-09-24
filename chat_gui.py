import PySimpleGUI as sg
import requests
import json
import os

MCP_SERVER_URL = "http://127.0.0.1:8080/rpc"

# ----- Funciones -----
def rpc_request(method, params=None):
    """Enviar request al servidor MCP."""
    payload = {"method": method, "params": params or {}}
    try:
        response = requests.post(MCP_SERVER_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def log_update(window, text):
    """Mostrar mensajes en el log."""
    window["-LOG-"].print(text)

# ----- Layout -----
sg.theme("DarkBlue14")

menu_def = [["Archivo", ["Salir"]], ["Ayuda", ["Comandos"]]]

layout = [
    [sg.Menu(menu_def)],
    [sg.Text("MCP Othello Chatbot", font=("Helvetica", 16), justification="center", expand_x=True)],
    [sg.Multiline(size=(80, 20), key="-LOG-", autoscroll=True, disabled=True, expand_x=True, expand_y=True)],
    [sg.Text("Escribe tu mensaje:"), sg.Input(key="-INPUT-", expand_x=True), sg.Button("Enviar")],
    [
        sg.Button("📂 Cargar Partida", size=(15,1)),
        sg.Button("🔍 Analizar", size=(10,1)),
        sg.Button("🎲 Simular", size=(10,1)),
        sg.Button("📑 Exportar", size=(10,1)),
        sg.Button("❌ Salir", size=(10,1))
    ]
]

window = sg.Window("MCP Othello Chatbot", layout, resizable=True, finalize=True)

# ----- Lógica de eventos -----
current_game_id = None

while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, "Salir", "❌ Salir"):
        break

    if event == "Enviar":
        user_input = values["-INPUT-"].strip()
        if user_input:
            log_update(window, f"> {user_input}")
            # Aquí podrías mapear /ask o comandos personalizados
            result = rpc_request("chat_message", {"text": user_input})
            log_update(window, json.dumps(result, indent=2))
            window["-INPUT-"].update("")

    if event == "📂 Cargar Partida":
        path = sg.popup_get_file("Selecciona el archivo de partida", file_types=(("JSON Files", "*.json"),))
        if path:
            result = rpc_request("load_game", {"path": path})
            current_game_id = result.get("game_id")
            log_update(window, f"Cargada partida: {json.dumps(result, indent=2)}")

    if event == "🔍 Analizar":
        if current_game_id:
            result = rpc_request("analyze_game", {"game_id": current_game_id})
            log_update(window, f"Análisis: {json.dumps(result, indent=2)}")
        else:
            sg.popup_error("Primero carga una partida")

    if event == "🎲 Simular":
        if current_game_id:
            n = sg.popup_get_text("¿Cuántas jugadas simular?", default_text="10")
            if n and n.isdigit():
                result = rpc_request("simulate_game", {"game_id": current_game_id, "n": int(n)})
                log_update(window, f"Simulación: {json.dumps(result, indent=2)}")
        else:
            sg.popup_error("Primero carga una partida")

    if event == "📑 Exportar":
        if current_game_id:
            result = rpc_request("export_report", {"game_id": current_game_id})
            log_update(window, f"Exportado: {json.dumps(result, indent=2)}")
        else:
            sg.popup_error("Primero carga una partida")

    if event == "Comandos":
        sg.popup("Comandos disponibles",
                 "/ask <texto>\n/load_local_game <archivo>\n/analyze <id>\n/simulate <id> <n>\n/export <id>",
                 title="Ayuda")

window.close()
