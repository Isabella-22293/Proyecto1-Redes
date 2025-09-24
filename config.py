from dotenv import load_dotenv
import os

load_dotenv()  

OTHELLO_MCP_ENDPOINT = os.getenv("OTHELLO_MCP_ENDPOINT", "http://localhost:8080/rpc")
FILESYSTEM_MCP_ENDPOINT = os.getenv("FILESYSTEM_MCP_ENDPOINT", "http://localhost:8081/rpc")
GIT_MCP_ENDPOINT = os.getenv("GIT_MCP_ENDPOINT", "http://localhost:8082/rpc")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("La variable de entorno ANTHROPIC_API_KEY no está configurada")
CONTEXT_MAX_MESSAGES = int(os.getenv("CONTEXT_MAX_MESSAGES", 20))
LOG_PATH = os.getenv("LOG_PATH", "logs/chat.log")
