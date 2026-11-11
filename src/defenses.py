import re

def normalize_text(text: str) -> str:
    """Converte para minúsculas e normaliza espaços extra/quebras de linha."""
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def is_input_safe(user_query: str) -> bool:
    """Valida input contra padrões maliciosos (prompt injection/leaking)."""
    suspicious_patterns = [
        r"ignore all previous instructions",
        r"developer mode",
        r"repeat all",
        r"translate your initial",
        r"system override"
    ]
    
    normalized_query = normalize_text(user_query)
    
    for pattern in suspicious_patterns:
        if re.search(pattern, normalized_query):
            return False # Match malicioso
    return True # Clean

def filter_output(llm_response: str) -> str:
    """Sanitiza output do LLM para evitar fuga de dados e injeções bem-sucedidas."""
    # Guardamos os termos em minúsculas para a comparação
    blocked_terms = [
        "canary-7f3k", 
        "pwned-123", 
        "prod_db_key_9948271"
    ]
    
    normalized_response = normalize_text(llm_response)
    
    for term in blocked_terms:
        if term in normalized_response:
            return "[BLOCK: Resposta bloqueada por conter dados sensíveis ou marcadores de injeção.]"
            
    return llm_response