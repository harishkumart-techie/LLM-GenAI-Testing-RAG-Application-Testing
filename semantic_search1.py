import requests
import chromadb


# -----------------------------------------
# 1. Connect to ChromaDB
# -----------------------------------------

client = chromadb.PersistentClient(
    path="./leave_policy_db"
)

collection = client.get_collection(
    name="leave_policy"
)


# -----------------------------------------
# 2. Create embedding
# -----------------------------------------

def create_embedding(text):

    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )

    response.raise_for_status()

    return response.json()["embedding"]


# -----------------------------------------
# 3. Ask user question
# -----------------------------------------

question = input("Ask your question: ")


# -----------------------------------------
# 4. Convert question into embedding
# -----------------------------------------

query_embedding = create_embedding(question)


# -----------------------------------------
# 5. Semantic search
# -----------------------------------------

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)


# -----------------------------------------
# 6. Get relevant documents
# -----------------------------------------

documents = results["documents"][0]

context = "\n\n".join(documents)


# -----------------------------------------
# 7. Send context + question to LLM
# -----------------------------------------

prompt = f"""
You are a helpful question-answering assistant.

Answer the user's question using ONLY the information provided
in the context below.

Do not reproduce the entire document.

Give a short, direct answer.

If the answer is not present in the context, say:
"I could not find the answer in the provided document."

Context:
-------------------------
{context}
-------------------------

Question:
{question}

Answer:
"""


# -----------------------------------------
# 8. Call Ollama LLM
# -----------------------------------------

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }
)

response.raise_for_status()

answer = response.json()["response"]


# -----------------------------------------
# 9. Display final answer
# -----------------------------------------

print("\n===== ANSWER =====\n")
print(answer.strip())

print("\n===== SOURCE =====\n")
print("Employee Leave Policy")