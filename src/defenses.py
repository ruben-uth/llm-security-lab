# defenses.py
import re

def filter_input(user_query: str) -> bool:
    """Valida input contra padrões maliciosos (prompt injection/leaking)."""
    suspicious_patterns = [
        r"ignore all previous instructions",
        r"developer mode",
        r"repeat all",
        r"translate your initial",
        r"system override"
    ]
    query_lower = user_query.lower()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, query_lower):
            return False # Match malicioso
    return True # Clean

def filter_output(llm_response: str) -> str:
    """Sanitiza output do LLM para evitar fuga de dados e injeções bem-sucedidas."""
    blocked_terms = [
        "CANARY-7F3K", 
        "PWNED-123", 
        "prod_db_key_9948271"
    ]
    
    for term in blocked_terms:
        if term in llm_response:
            return "[BLOCK: Resposta bloqueada por conter dados sensíveis ou marcadores de injeção.]"
            
    return llm_response