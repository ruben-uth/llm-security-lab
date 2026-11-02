# 🛡️ LLM Security Lab: RAG Vulnerability Assessment & Mitigation

This project is a cybersecurity laboratory focused on assessing and mitigating vulnerabilities in **Retrieval-Augmented Generation (RAG)** systems powered by Large Language Models (LLMs). 

The main objective is to demonstrate, in a local and controlled environment, how vulnerabilities from the **OWASP Top 10 for LLM Applications** can be exploited, and how to implement defense layers (Input/Output Filters) to secure the architecture.

## Key Vulnerabilities Tested (OWASP)

*   **LLM01: Prompt Injection (Direct & Indirect):** Tests focused on Direct Injections via chat and Indirect Injections through poisoned documents (RAG Data Poisoning), manipulating the LLM to bypass restrictions.
*   **LLM06: Sensitive Information Disclosure:** Secret extraction attempts (Prompt Leaking), where the attacker uses extraction techniques to reveal confidential data (*Canary Tokens*) hardcoded in the *System Prompt*.

## Tech Stack & Architecture

*   **LLM Engine:** LLaMA 3.1 (via local Ollama).
*   **Vector Database:** ChromaDB (embedding storage and retrieval).
*   **Embeddings:** `all-MiniLM-L6-v2` (HuggingFace `sentence-transformers`).
*   **Evaluation Engine:** Custom Python framework based on YAML files to orchestrate structured attack payloads.

## Security Evaluation Results

The testing engine orchestrates 8 specific attacks. The results demonstrate the impact of implementing a *Zero Trust* architecture around the LLM:

| Scenario | Attack Success Rate (Vulnerability) |
| :--- | :--- |
| **Baseline (System without defenses)** | **50.0%** |
| **Secured (Input/Output Filters)** | **0.0%** |

*Note: The defenses act as a firewall, analyzing malicious patterns in the user's prompt (Input Filter) and blocking sensitive data leakage in the model's response (Output Filter).*

## Setup & Execution

### 1. Requirements and Installation
The project uses an isolated Python virtual environment and requires [Ollama](https://ollama.com/) installed with the `llama3.1` model pulled (`ollama run llama3.1`).

```bash
# Activate the virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (copy the template and adjust if needed)
copy .env.example .env
```

### 2. The Evaluation Engine (Execution Modes)
To ensure development efficiency and save computational resources (CPU/GPU), the evaluation engine has two operation modes, controlled by environment variables:

*   **MOCK Mode (`LLM_MODE=mock`):** Instantly simulates LLM mechanics through static rules. Ideal for integration testing (CI/CD) and RAG architecture debugging without computational cost.
*   **OLLAMA Mode (`LLM_MODE=ollama`):** Uses the actual local AI model for natural language processing and final validation of the attack surface.

### 3. Test the Vulnerability (Baseline - 50% Success)
To simulate the system in its natural (vulnerable) state, we disable the defenses:
```cmd
set LLM_MODE=ollama
set USE_DEFENSES=false
python evaluate.py
```

### 4. Test the Mitigation (Secured - 0% Success)
To activate the security barriers that block prompt injections and data leakage:
```cmd
set LLM_MODE=ollama
set USE_DEFENSES=true
python evaluate.py
```

## Project Structure

*   `/attacks` - YAML attack catalog defining malicious prompts and success criteria.
*   `/src` - Application core logic:
    *   `rag.py` - Document ingestion and context-augmented prompt building.
    *   `llm.py` - Ollama integration (Real mode) or test bypass (Mock mode).
    *   `defenses.py` - Input Filters (Regex) and Output Filters (Data Masking).
*   `evaluate.py` - Evaluation orchestrator that computes attack success metrics.