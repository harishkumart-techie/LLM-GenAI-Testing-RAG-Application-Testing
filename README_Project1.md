# HR Leave Policy Assistant: LLM, RAG & Agentic AI Testing

A local proof-of-concept that explores how a Large Language Model (LLM) can answer questions about a company leave policy using Retrieval-Augmented Generation (RAG), semantic search, and tool calling.

The project evolves from retrieving relevant policy text to generating grounded answers, extracting policy information into JSON, and building an agent that can use tools for policy lookup and employee leave-balance queries. Later versions also demonstrate a FastAPI endpoint and a human-approval status for leave requests.

> **Project status:** Learning / prototype project. Validate the code, dependencies, data, and security settings before using it in any real environment. The included code has not been independently production-tested.

## Objectives

- Explore semantic search over a PDF policy document.
- Convert a user question into an embedding and retrieve relevant text chunks from ChromaDB.
- Use an LLM to produce a concise answer based on retrieved context.
- Instruct the model not to invent policy details when the answer is absent from the retrieved context.
- Experiment with structured policy extraction into JSON.
- Explore LLM tool/function calling and agent workflows.
- Expose an agent through a FastAPI endpoint in the later version.
- Demonstrate a leave-request tool that returns a pending-human-approval status rather than claiming that leave has been approved.

## Architecture

### Basic semantic search and RAG

1. Read the sample leave-policy PDF.
2. Extract text and split it into simple text chunks.
3. Generate embeddings using Ollama and `nomic-embed-text`.
4. Store chunks and vectors in a persistent ChromaDB collection named `leave_policy`.
5. Embed the user's question and retrieve the top three relevant chunks.
6. Pass the retrieved context and question to `llama3.2` through Ollama.
7. Return a concise answer, with an instruction to say when the answer cannot be found in the provided context.

### Agentic workflow

The later LangChain/LangGraph implementation connects an LLM to tools for:
- Looking up a specific employee's leave balance.
- Searching the leave policy using the ChromaDB retriever.
- Preparing a leave request marked `PENDING_HUMAN_APPROVAL`.

The FastAPI version exposes a `POST /ask` endpoint. A helper function is present as an integration point for n8n, but the webhook URL is not configured in the supplied code.

## Technology stack

- **Python**
- **Ollama** for local model inference
- **Llama 3.2** (`llama3.2`) for answer generation and tool-calling experiments
- **nomic-embed-text** for embeddings
- **ChromaDB** for persistent vector storage
- **LangChain** for LLM, embedding, and retriever integration
- **LangGraph** for the agent workflow
- **FastAPI** and **Uvicorn** for the API version
- **Pypdf** for PDF text extraction
- **PostgreSQL / Psycopg** for the database-backed employee lookup in the later version
- **Requests** for local Ollama API calls and the optional n8n integration point

## Repository files

| File | Purpose |
|---|---|
| `sample_company_leave_policy.pdf` | Sample policy document used as the retrieval source. Ensure you have the right to publish it before committing it. |
| `embeddings.py` | Extracts PDF text, creates simple chunks, generates embeddings, and stores them in ChromaDB. |
| `semantic_search.py` | Embeds a question and prints the top retrieved policy chunks. |
| `semantic_search1.py` | Retrieves relevant chunks and asks the LLM to produce a concise answer from the context. |
| `rag_leave_assistant.py` | Basic RAG question-answering flow using retrieved policy chunks as context. |
| `leave_policy_extractor.py` | Sends the policy text to the LLM and requests structured JSON output for selected policy fields. |
| `v4_leave_Tool_function_calling.py` | Early Ollama function-calling example for looking up sample employee leave balances. |
| `v5_agent1.py` | LangGraph agent with tools for leave-balance lookup and policy search. |
| `v6_api.py` | Later agent version with PostgreSQL-backed leave lookup, policy retrieval, a leave-request tool, and a FastAPI endpoint. |
| `v6_v8_app.py` | Similar FastAPI / agent implementation and n8n integration placeholder. |
| `leave_policy_db/` | Local ChromaDB persistence directory. Usually regenerate this locally instead of committing database binaries. |

Some files are alternative iterations of the same prototype rather than separate applications. The database-backed versions require a separately configured PostgreSQL database and an `employees` table.

## Prerequisites

1. Install Python 3.10 or later (use a version compatible with the installed libraries).
2. Install [Ollama](https://ollama.com/).
3. Pull the models used by the scripts:

   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

4. Start Ollama and confirm that its local API is available at `http://localhost:11434`.
5. Open a terminal in the project directory and create a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   ```

6. Install the dependencies needed for the basic RAG scripts:

   ```bash
   pip install requests chromadb pypdf
   ```

   For the LangChain/LangGraph agent versions, install the additional packages:

   ```bash
   pip install langchain-ollama langchain-chroma langchain-core langgraph fastapi "uvicorn[standard]" pydantic
   ```

   For the PostgreSQL-backed API versions, also install:

   ```bash
   pip install "psycopg[binary]"
   ```

These are package groups inferred from the imports in the supplied scripts, not a pinned, verified lockfile. For a reproducible setup, create and test a `requirements.txt` in your environment.

## Running the basic RAG flow

Run commands from the directory containing the Python files and the PDF.

### 1. Build the vector collection

```bash
python embeddings.py
```

This reads `sample_company_leave_policy.pdf`, creates embeddings, and writes them to `./leave_policy_db`. Run this before using scripts that expect the collection to exist. If you rebuild the collection, ensure that old records are handled appropriately; the sample script uses chunk indices as IDs and does not implement a full reset/update strategy.

### 2. Inspect semantic-search results

```bash
python semantic_search.py
```

Enter a question about the policy. The script prints retrieved text chunks rather than a synthesized answer.

### 3. Ask a question using RAG

```bash
python semantic_search1.py
```

This retrieves the top three chunks, sends them with the question to the LLM, and prints the generated answer and a generic source label.

Alternatively, try:

```bash
python rag_leave_assistant.py
```

### 4. Extract policy fields as JSON

```bash
python leave_policy_extractor.py
```

The script asks the LLM to return selected fields such as leave type, days per year, carry-forward status, and maximum balance. Always validate generated JSON and compare extracted values with the source document.

## Running the agent / API versions

The early function-calling and LangGraph scripts are separate experiments:

```bash
python v4_leave_Tool_function_calling.py
python v5_agent1.py
```

The later FastAPI implementation is intended to be started with Uvicorn, for example:

```bash
uvicorn v6_v8_app:api --host 127.0.0.1 --port 8000 --reload
```

Then open `http://127.0.0.1:8000/docs` to explore the API documentation and the `POST /ask` endpoint.

**Important:** The `v6_api.py` and `v6_v8_app.py` versions require PostgreSQL configuration and a compatible `employees` table. Do not run these versions until you have removed embedded credentials, configured environment variables, and verified the database schema. The leave-request tool shown in the supplied code returns a pending-approval result; it does not implement a real HR approval system or persist a leave request.

## Example questions to try

Use questions that are answerable from the sample policy, such as:

- What is the annual entitlement for a specified leave type?
- Can unused leave be carried forward?
- Is there a maximum leave balance?
- What eligibility conditions are stated in the policy?
- Does the provided policy mention a particular leave scenario?

For the agent versions, if you configure a safe test database with synthetic records, you can also ask about a test employee's leave balance. Do not use real employee information in a public demo.

## LLM & GenAI testing opportunities

This project can be used as a foundation for documenting and performing QA checks such as:

| Test area | Example validation |
|---|---|
| Retrieval relevance | Does the top-K result contain the policy passage relevant to the question? |
| Groundedness / faithfulness | Is each factual claim supported by retrieved context? |
| Hallucination resistance | Does the assistant abstain when the policy does not contain the answer? |
| Answer relevance | Does the response answer the question asked without dumping whole chunks? |
| Citation / source traceability | Can a response be traced to the source page or retrieved chunk? The current scripts provide limited source traceability. |
| Boundary and negative testing | Try ambiguous, incomplete, out-of-scope, and unsupported questions. |
| Regression testing | Re-run a fixed set of questions after changing prompts, chunking, embeddings, retrieval settings, or models. |
| Extraction validation | Compare JSON fields produced by the LLM with values manually verified from the policy. |
| Tool selection | Check whether the agent chooses policy search, balance lookup, or leave-request preparation appropriately. |
| Tool argument validation | Test missing, invalid, or unsupported employee IDs and leave types. |
| Human approval guardrail | Verify that a leave request is represented as pending and never described as approved. |
| API validation | Test valid and invalid request bodies, unavailable dependencies, and error handling. |
| Security | Test prompt injection in questions and documents, unauthorized data access, and sensitive-data exposure using synthetic data only. |

These are recommended test ideas, not a claim that all tests have already been implemented or passed. Record actual results in a test report before presenting them as completed work.

## Current limitations

- Text chunking is basic and based on blank-line separation; it is not a robust layout-aware or token-aware chunking strategy.
- Retrieval uses a fixed top-K value of three; there is no measured retrieval benchmark in the supplied code.
- The scripts do not include an automated test suite or a pinned dependency file.
- Source attribution is limited; robust page/chunk-level citations would need to be added.
- Model output can still be incorrect. Prompt instructions alone do not guarantee grounded answers.
- The n8n integration helper is not configured or called by the supplied API flow.
- The PostgreSQL-backed versions depend on external database setup.
- The human-approval tool is a demonstration response, not a complete workflow with persisted requests and an approval interface.
- Performance, security, privacy, and production readiness have not been established.

## Security and publishing checklist

Before making this repository public:

- [ ] Remove all passwords, tokens, connection strings, and other secrets from source code and Git history.
- [ ] Read database credentials from environment variables or a secret manager; never commit real credentials.
- [ ] Replace real names, employee IDs, balances, and company information with synthetic data.
- [ ] Confirm that you have permission to publish the PDF and all included sample data.
- [ ] Do not commit local database files, logs, virtual environments, caches, or private configuration files.
- [ ] Add a `.gitignore` and a safe `.env.example` containing placeholders only.
- [ ] Run a secret scan and review the files being committed.
- [ ] Document only test results you have actually observed.

## Learning outcome

This project demonstrates a practical learning path from embeddings and semantic retrieval to RAG question answering, structured extraction, LLM tool calling, and a basic agent/API design. It also provides a useful base for adding a repeatable GenAI QA regression suite with golden questions, expected evidence, evaluation metrics, and release criteria.

## Disclaimer

This is an educational prototype. The sample policy and any sample employee data should be treated as demo data only. It is not an official HR system and must not be used to make real employment or leave decisions.
