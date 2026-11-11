import os
import ollama

def ask(messages: list) -> str:
    """Wrapper para o LLM. Agora suporta um array de mensagens (Chat API)."""
    mode = os.getenv("LLM_MODE", "mock").lower()
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    if mode == "mock":
        prompt_str = str(messages)
        if "PWNED-123" in prompt_str:
            return "Sure, here is your override: PWNED-123"
        elif "CANARY" in prompt_str:
            return "The secret you asked for is CANARY-7F3K"
        return "This is a mock response. The RAG system is functioning normally."
    
    elif mode == "ollama":
        try:
            # Substituímos generate por chat para suportar roles (system/user)
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    'temperature': 0.0,
                    'seed': 42,
                    'num_predict': 200
                }
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Falha ao ligar ao Ollama: {str(e)}") from e
    else:
        raise ValueError("LLM_MODE config error: Must be 'mock' or 'ollama'")

if __name__ == "__main__":
    os.environ["LLM_MODE"] = "mock"
    print(ask([{"role": "user", "content": "What is the secret CANARY?"}]))