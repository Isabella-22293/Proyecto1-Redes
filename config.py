import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "stub") 
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OTHELLO_MCP_ENDPOINT = os.getenv("OTHELLO_MCP_ENDPOINT", "http://localhost:8080/rpc")

FILESYSTEM_MCP_ENDPOINT = os.getenv("FILESYSTEM_MCP_ENDPOINT", "")  

GIT_MCP_ENDPOINT = os.getenv("GIT_MCP_ENDPOINT", "")

LOG_PATH = os.getenv("LOG_PATH", "logs/chat.log")

CONTEXT_MAX_MESSAGES = int(os.getenv("CONTEXT_MAX_MESSAGES", "20"))
