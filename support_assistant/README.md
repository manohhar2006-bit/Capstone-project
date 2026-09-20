# Zepto Support Assistant

Module 3 of the IIT Patna AI/ML Capstone.

This module implements an offline Zepto policy support assistant using document
embeddings, ChromaDB retrieval, LangGraph orchestration, structured Pydantic
responses, and a FastAPI `/ask` endpoint.

The graded baseline uses deterministic `MOCK_LLM` behavior and does not require
an API key or network access for inference.

---

## Project Structure

```text
support_assistant/
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
├── ingest.py
├── prompt.py
├── graph.py
├── models.py
├── main.py
├── Dockerfile
└── README.md
```

`chroma_db/` is generated locally when the corpus is ingested.

---

## Module Requirements Covered

This implementation covers:

1. Eight Zepto policy documents loaded and embedded.
2. `all-MiniLM-L6-v2` sentence-transformer embeddings.
3. ChromaDB vector storage.
4. Structured role/context/task/format/length prompt.
5. Explicit negative constraint.
6. Few-shot example.
7. LangGraph `StateGraph` orchestration.
8. Three graph nodes:
   - `classify_intent`
   - `retrieve_and_answer`
   - `direct_answer`
9. Conditional routing between policy and general questions.
10. Pydantic structured response:
    - `answer`
    - `sources`
    - `confidence`
11. FastAPI `POST /ask` endpoint.
12. Local Docker build and run.
13. Deterministic offline `MOCK_LLM` baseline.

---

## Architecture

```text
                    Customer Query
                          |
                          v
                 +------------------+
                 | classify_intent  |
                 +------------------+
                    /            \
                   /              \
        policy_question        general_question
               |                     |
               v                     v
    +-----------------------+   +---------------+
    | retrieve_and_answer   |   | direct_answer |
    +-----------------------+   +---------------+
               |
               v
        ChromaDB Retrieval
               |
               v
        Top-3 policy chunks
               |
               v
        Answer generation
               |
               +-------------------+
                                   |
                                   v
                         Pydantic Response
                                   |
                                   v
                             FastAPI /ask
```

### Data Flow

```text
Zepto policy documents
        |
        v
      docs/
        |
        v
     ingest.py
        |
        +--> SentenceTransformer
        |      all-MiniLM-L6-v2
        |
        v
     ChromaDB
        |
        v
    graph.py
        |
        +--> classify_intent
        |
        +--> retrieve_and_answer
        |
        +--> direct_answer
        |
        v
    models.py
        |
        v
     FastAPI
      /ask
```

---

## File Responsibilities

### `ingest.py`

Loads all eight policy documents from `docs/`, creates embeddings using
`all-MiniLM-L6-v2`, normalizes the embeddings, and stores the documents,
embeddings, IDs, and metadata in the ChromaDB collection
`zepto_policies`.

### `prompt.py`

Contains the structured support-assistant prompt with:

- Role
- Context
- Task
- Format
- Length
- Negative constraint
- Few-shot example

The prompt instructs the assistant to use only the retrieved Zepto policy
context and not invent policy details.

### `graph.py`

Contains the LangGraph workflow and the three required nodes:

- `classify_intent`
- `retrieve_and_answer`
- `direct_answer`

The graph uses conditional routing after intent classification.

### `models.py`

Defines the Pydantic response schema:

```text
answer: str
sources: list[str]
confidence: float
```

The confidence value is constrained to the range `0.0` to `1.0`.

### `main.py`

Creates the FastAPI application and exposes:

```text
POST /ask
```

Request body:

```json
{
  "query": "string"
}
```

### `Dockerfile`

Builds a local container containing the application, policy corpus,
embedding dependencies, ChromaDB ingestion, and FastAPI server.

---

## Retrieval and Routing

The default graded behavior uses `MOCK_LLM=1` or an unset `MOCK_LLM`.

Intent classification uses a deterministic keyword heuristic.

The policy keywords are:

```text
delivery
return
refund
membership
tracking
cancel
gift card
support hours
```

Policy questions are sent to `retrieve_and_answer`.

General questions are sent to `direct_answer`.

For policy questions, retrieval is always performed using the query embedding
and ChromaDB top-3 similarity search.

---

## MOCK_LLM Behavior

The graded baseline is fully deterministic and offline.

When:

```text
MOCK_LLM=1
```

or the variable is not set:

- intent classification uses the keyword heuristic
- retrieval uses ChromaDB
- the answer uses the retrieved top chunk
- general questions use a fixed canned response
- no LLM API call is required

The policy retrieval mock response follows the format:

```text
Based on the retrieved context: {top_chunk_snippet}
```

The general-question mock response is:

```text
I can only answer questions about Zepto policies right now.
```

The mock confidence value is:

```text
1.0
```

---

## Optional Real-LLM Path

The application also contains an optional real-LLM path.

Set:

```text
MOCK_LLM=0
```

and provide:

```text
GROQ_API_KEY
```

The real path uses the Groq client and the model configured in `graph.py`.

The graded capstone baseline does not depend on this optional path.

---

## Running Locally

From the `support_assistant` directory:

```powershell
python ingest.py
```

Then start the API:

```powershell
uvicorn main:app --reload --port 8000
```

The API is available at:

```text
http://127.0.0.1:8000
```

---

## API Usage

Endpoint:

```text
POST /ask
```

### Example 1: Policy Retrieval Query

Request:

```json
{
  "query": "What is the delivery fee for an order below INR 149?"
}
```

Raw response from the local FastAPI test:

```json
{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer\u0027s delivery zone and current order volume. Standard del","sources":["doc_01","doc_05","doc_07"],"confidence":1.0}
```

This query is classified as a policy question and uses ChromaDB retrieval.

### Example 2: General Query

Request:

```json
{
  "query": "What is the capital of India?"
}
```

Raw response from the local FastAPI test:

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

This query is classified as a general question and does not perform policy
retrieval.

---

## Docker

Build the image from the `support_assistant` directory:

```powershell
docker build -t zepto-support-assistant .
```

Run the container:

```powershell
docker run --name zepto-support-assistant-container -p 7860:7860 zepto-support-assistant
```

The container starts Uvicorn on:

```text
http://localhost:7860
```

The FastAPI endpoint remains:

```text
POST /ask
```

---

## Pipeline Summary

```text
1. Load 8 Zepto policy documents
2. Generate embeddings using all-MiniLM-L6-v2
3. Store embeddings in ChromaDB
4. Receive a customer query through FastAPI
5. Classify the intent
6. Route using LangGraph
7. Retrieve top-3 policy chunks for policy questions
8. Generate the deterministic mock answer
9. Validate the response with Pydantic
10. Return JSON through /ask
```

---

## Mock Baseline Verification

The completed local verification confirmed:

```text
Policy query
    -> policy_question
    -> ChromaDB retrieval
    -> sources returned
    -> confidence = 1.0

General query
    -> general_question
    -> no retrieval
    -> sources = []
    -> confidence = 1.0
```