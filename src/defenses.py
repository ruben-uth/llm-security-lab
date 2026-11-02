import re

def filter_input(user_query: str) -> bool:
    """
    Verifica se a pergunta do utilizador contém padrões maliciosos conhecidos.
    Retorna True se for seguro, False se for detetado um ataque.
    """
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
            return False # Ataque detetado
    return True # Seguro

def filter_output(llm_response: str) -> str:
    """
    Analisa a resposta do LLM antes de a devolver ao utilizador.
    Substitui a resposta por um aviso se detetar marcadores de injeção ou dados sensíveis.
    """
    blocked_terms = [
        "CANARY-7F3K", 
        "PWNED-123", 
        "prod_db_key_9948271"
    ]
    
    for term in blocked_terms:
        if term in llm_response:
            return "[BLOCK: Resposta bloqueada por conter dados sensíveis ou marcadores de injeção.]"
            
    return llm_response