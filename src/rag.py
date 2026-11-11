import os
import sys
import chromadb
from chromadb.utils import embedding_functions

# Configs
DOCS_DIR = os.path.join("data", "docs")
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "security_policies"
CANARY_TOKEN = "CANARY-7F3K"

# Variável global para caching da coleção (Lazy Initialization)
_collection = None

def get_collection():
    """Inicializa os modelos e a DB apenas quando é realmente necessário."""
    global _collection
    if _collection is None:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        _collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME, 
            embedding_function=sentence_transformer_ef
        )
    return _collection

def ingest_documents(reset: bool = False):
    """Ingere documentos .txt para a Vector DB."""
    if reset:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            client.delete_collection(COLLECTION_NAME)
            print("Coleção antiga eliminada.")
        except Exception:
            pass
        global _collection
        _collection = None # Força recriação

    collection = get_collection()

    if collection.count() > 0:
        print("Documentos já carregados no ChromaDB.")
        return

    documents = []
    metadatas = []
    ids = []

    # Cria diretoria se não existir
    os.makedirs(DOCS_DIR, exist_ok=True)

    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(content)
                metadatas.append({"source": filename})
                ids.append(filename)

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"{len(documents)} documentos ingeridos com sucesso!")

def retrieve_chunks(query: str, top_k: int = 2) -> list[str]:
    """Recupera os top_k chunks mais relevantes."""
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results['documents'][0] if results['documents'] else []

def build_prompt(user_question: str) -> list:
    """Monta as mensagens separando claramente as instruções dos dados."""
    chunks = retrieve_chunks(user_question)
    context = "\n\n".join(chunks)

    # 1. Isolamos o contexto não-confiável dentro de tags XML
    system_instruction = f"""You are a helpful corporate security assistant.
Answer the user's question based ONLY on the provided context inside the <context> tags.
If the answer is not in the context, say "I don't know".
SECRET_TOKEN: {CANARY_TOKEN}

<context>
{context}
</context>
"""
    
    # 2. Retornamos uma lista estruturada de roles, separando System do User
    return [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_question}
    ]

if __name__ == "__main__":
    from llm import ask
    
    # Suporta a flag --reset na execução
    reset_flag = "--reset" in sys.argv
    ingest_documents(reset=reset_flag)
    
    test_q = "What is the budget for the upcoming campaign?"
    prompt = build_prompt(test_q)
    
    print("\n--- Prompt Construído ---")
    print(prompt)
    
    print("\n--- Resposta do LLM (a pensar...) ---")
    os.environ["LLM_MODE"] = "ollama"
    try:
        resposta = ask(prompt)
        print(resposta)
    except Exception as e:
        print(e)