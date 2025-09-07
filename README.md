# Othello Coach MCP

## Resumen
Servidor MCP que analiza partidas de Othello y un chatbot anfitrión que:
- Se conecta a un LLM (OpenAI por defecto);
- Mantiene contexto de conversación;
- Registra logs;
- Integra MCP Filesystem y Git (ejemplos).

## Instalación
```bash
git clone <https://github.com/Isabella-22293/Proyecto1-Redes.git>
cd Proyecto1-Redes
python -m venv .venv
. .venv/bin/activate o .venv\\Scripts\\activate en Windows
pip install -r requirements.txt
