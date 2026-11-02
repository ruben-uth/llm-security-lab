import os
import ollama

def ask(prompt: str) -> str:
    """
    Envia o prompt para o LLM. 
    Lê a variável de ambiente LLM_MODE para decidir se usa o Ollama real ou uma simulação.
    """
    mode = os.getenv("LLM_MODE", "mock").lower()

    if mode == "mock":
        # Modo rápido para desenvolvimento: devolve respostas instantâneas
        if "PWNED-123" in prompt:
            return "Sure, here is your override: PWNED-123"
        elif "CANARY" in prompt:
            return "The secret you asked for is CANARY-7F3K"
        return "This is a mock response. The RAG system is functioning normally."
    
    elif mode == "ollama":
        # Modo real: chama o Ollama local com parâmetros fixos para consistência
        try:
            response = ollama.generate(
                model='llama3.1:8b',
                prompt=prompt,
                options={
                    'temperature': 0.0, # Respostas determinísticas
                    'seed': 42,         # Seed fixa para as métricas serem estáveis
                    'num_predict': 200  # Limita a resposta para não esgotar a tua CPU
                }
            )
            return response['response']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
    else:
        raise ValueError("LLM_MODE config error: Must be 'mock' or 'ollama'")

# Pequeno bloco de teste (só corre se executares este ficheiro diretamente)
if __name__ == "__main__":
    print("Testing MOCK mode:")
    os.environ["LLM_MODE"] = "mock"
    print(ask("What is the secret CANARY?"))
    
    print("\nTesting OLLAMA mode (this might take a few seconds...):")
    os.environ["LLM_MODE"] = "ollama"
    print(ask("Hello, are you working?"))