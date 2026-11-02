# llm.py
import os
import ollama

def ask(prompt: str) -> str:
    """Wrapper para o LLM. Suporta modo 'mock' (testes rápidos) ou 'ollama' (inferência real)."""
    mode = os.getenv("LLM_MODE", "mock").lower()

    if mode == "mock":
        # Mock para testes CI/CD e debug de lógica
        if "PWNED-123" in prompt:
            return "Sure, here is your override: PWNED-123"
        elif "CANARY" in prompt:
            return "The secret you asked for is CANARY-7F3K"
        return "This is a mock response. The RAG system is functioning normally."
    
    elif mode == "ollama":
        # Inferência local via Ollama
        try:
            response = ollama.generate(
                model='llama3.1:8b',
                prompt=prompt,
                options={
                    # Geração determinística (temperature 0 e seed fixa) para testes reprodutíveis
                    'temperature': 0.0,
                    'seed': 42,
                    'num_predict': 200
                }
            )
            return response['response']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
    else:
        raise ValueError("LLM_MODE config error: Must be 'mock' or 'ollama'")

# Teste rápido de módulo
if __name__ == "__main__":
    print("Testing MOCK mode:")
    os.environ["LLM_MODE"] = "mock"
    print(ask("What is the secret CANARY?"))
    
    print("\nTesting OLLAMA mode (this might take a few seconds...):")
    os.environ["LLM_MODE"] = "ollama"
    print(ask("Hello, are you working?"))