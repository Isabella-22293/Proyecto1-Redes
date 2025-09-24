import os
import pytest
from chatbot_host_adapter import ChatbotHost  # ahora usamos el wrapper

def test_commands_parsing(tmp_path):
    log_file = tmp_path / "chat.log"
    host = ChatbotHost(log_file=str(log_file))
    
    # prueba comando /fs write y /fs read
    host.handle_command("/fs write test.txt Hola Mundo")
    content = host.handle_command("/fs read test.txt")
    assert "Hola Mundo" in content
    
    # prueba comando /fs list
    files = host.handle_command("/fs list")
    assert "test.txt" in files
    
    # prueba comando /ask (stub)
    resp = host.handle_command("/ask ¿Hola?")
    assert isinstance(resp, str)
