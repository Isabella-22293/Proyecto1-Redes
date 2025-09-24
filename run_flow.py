import json
import subprocess
import time

# Ruta al archivo de la partida
game_file = "games/sample_game.json"

# Inicia el chatbot host como proceso
proc = subprocess.Popen(
    ["python", "chatbot_host.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

def send(cmd):
    """Enviar comando al chatbot host"""
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()
    time.sleep(1)  # espera a que el host procese

# 1️⃣ Cargar juego
send(f"/load_local_game {game_file}")

# 2️⃣ Leer game_id del output (espera un momento para que el host responda)
time.sleep(2)
output = ""
while True:
    line = proc.stdout.readline()
    if not line:
        break
    output += line
    if '"game_id"' in line:
        break

# Extraer game_id del JSON en la línea
game_id = None
for line in output.splitlines():
    if '"game_id"' in line:
        try:
            game_id = json.loads(line)["game_id"]
            break
        except:
            pass

if not game_id:
    print("No se pudo obtener game_id, abortando.")
    proc.kill()
    exit(1)

print(f"Game ID detectado: {game_id}")

# 3️⃣ Analizar partida
send(f"/analyze {game_id}")

# 4️⃣ Exportar reporte
send(f"/export {game_id}")

# 5️⃣ Finalizar chatbot
send("/exit")
proc.wait()
print("Flujo completado. Revisa la carpeta reports\\")
