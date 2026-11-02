import yaml
import json
import os
from src.llm import ask
from src.rag import build_prompt, ingest_documents
from src.defenses import filter_input, filter_output

ATTACKS_FILE = os.path.join("attacks", "attacks.yaml")
RESULTS_FILE = "results.json"

def load_attacks():
    with open(ATTACKS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_evaluation():
    print("Preparando RAG...")
    ingest_documents()
    
    attacks = load_attacks()
    results = {
        "total_attacks": len(attacks),
        "successful_attacks": 0,
        "success_rate_overall": 0.0,
        "category_breakdown": {},
        "details": []
    }

    mode = os.getenv('LLM_MODE', 'mock').upper()
    print(f"\nIniciando avaliação de {len(attacks)} ataques (Modo: {mode})...")
    
    for i, attack in enumerate(attacks, 1):
        print(f"[{i}/{len(attacks)}] Testando: {attack['id']}...")
        
        # --- NOVO BLOCO PROTEGIDO ---
        if not filter_input(attack['prompt']):
            response = "[BLOCK: Input rejeitado pela triagem de segurança]"
        else:
            # 2. RAG e LLM
            prompt = build_prompt(attack['prompt'])
            raw_response = ask(prompt)
            # 3. Filtro de Output
            response = filter_output(raw_response)
        
        # Verifica se o ataque teve sucesso procurando a string-chave na resposta
        is_successful = attack['success_if_contains'].lower() in response.lower()
        
        if is_successful:
            results["successful_attacks"] += 1

        # Estatísticas por categoria
        cat = attack['category']
        if cat not in results["category_breakdown"]:
            results["category_breakdown"][cat] = {"total": 0, "successes": 0}
        
        results["category_breakdown"][cat]["total"] += 1
        if is_successful:
            results["category_breakdown"][cat]["successes"] += 1

        # Guarda os detalhes do ataque
        results["details"].append({
            "id": attack['id'],
            "category": attack['category'],
            "successful": is_successful,
            "response_snippet": response.replace('\n', ' ')[:100] + "..."
        })

    # Calcula as percentagens finais
    if results["total_attacks"] > 0:
        results["success_rate_overall"] = round((results["successful_attacks"] / results["total_attacks"]) * 100, 2)
        for cat, data in results["category_breakdown"].items():
            data["success_rate"] = round((data["successes"] / data["total"]) * 100, 2)

    # Guarda os resultados num ficheiro JSON
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nAvaliação concluída! Taxa de Sucesso dos Ataques: {results['success_rate_overall']}%")
    print(f"Resultados detalhados guardados em {RESULTS_FILE}")

if __name__ == "__main__":
    run_evaluation()