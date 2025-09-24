import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if LLM_PROVIDER == "anthropic":
    from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

def query_llm(prompt: str, max_tokens: int = 200):
    if LLM_PROVIDER == "anthropic":
        resp = client.completions.create(
            model="claude-2",
            prompt=f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}",
            max_tokens_to_sample=max_tokens
        )
        return resp.completion
    else:
        return "LLM provider no soportado"
