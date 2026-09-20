Zepto Support Assistant

Module 3 of the IIT Patna AI/ML Capstone.

This module implements a retrieval-augmented Zepto policy support assistant using the eight provided policy documents, all-MiniLM-L6-v2 embeddings, ChromaDB retrieval, LangGraph orchestration, structured Pydantic responses, and a FastAPI /ask endpoint.

The graded baseline uses deterministic MOCK_LLM behavior and does not require an API key or external LLM for inference.

Project Structure

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

chroma_db/ is generated locally by the ingestion step and is intentionally not committed to GitHub because it can be recreated from the provided corpus with ingest.py.

Module Requirements Covered

This implementation covers the Module 3 requirements:

Eight Zepto policy documents loaded into the support-assistant corpus.

Document chunking using one chunk per document.

all-MiniLM-L6-v2 sentence-transformer embeddings.

ChromaDB vector storage using cosine similarity.

Structured prompt with Role, Context, Task, Format, and Length sections.

Explicit negative constraint and few-shot example.

LangGraph StateGraph orchestration with TypedDict state.

Three graph nodes:

classify_intent

retrieve_and_answer

direct_answer

Conditional routing between policy and general questions.

Top-3 ChromaDB retrieval for policy questions.

Pydantic structured response containing answer, sources, and confidence.

FastAPI POST /ask endpoint with request and response validation.

Deterministic offline MOCK_LLM baseline.

Optional real-LLM path with structured JSON validation and retry handling.

Local Docker build and run.

Knowledge Base / RAG Corpus

The docs/ directory contains the eight policy documents supplied for the capstone:

Doc 01 - Delivery
Doc 02 - Returns & Refunds
Doc 03 - Membership Tiers
Doc 04 - Order Tracking
Doc 05 - Order Cancellation
Doc 06 - Damaged/Missing
Doc 07 - Gift Cards
Doc 08 - Customer Support Hours

These documents form the knowledge base used by the retrieval-augmented generation (RAG) pipeline.

RAG Pipeline

                 Zepto Policy Documents
                         |
                         v
                    docs/*.txt
                         |
                         v
                      ingest.py
                         |
                         v
              all-MiniLM-L6-v2 Embeddings
                         |
                         v
                      ChromaDB
                  (cosine similarity)
                         ^
                         |
                  Query Embedding
                         ^
                         |
                    Customer Query
                         |
                         v
                   classify_intent
                         |
             +-----------+-----------+
             |                       |
      policy_question         general_question
             |                       |
             v                       v
   retrieve_and_answer        direct_answer
             |
             v
        Top-3 policy chunks
             |
             v
       Retrieved context
             |
             v
        Answer generation
             |
             v
      Pydantic response
             |
             v
          FastAPI /ask

RAG Components

docs/ — source knowledge corpus.

ingest.py — document loading, chunking, embedding, and ChromaDB indexing.

chroma_db/ — locally generated persistent vector store.

graph.py — query embedding, top-3 retrieval, routing, and answer generation.

prompt.py — structured context-grounded answer-generation prompt.

Architecture

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
        Query Embedding
               |
               v
        ChromaDB Top-3
               |
               v
      Retrieved Policy Context
               |
               v
        Answer Generation
               |
               v
       Pydantic Response
               |
               v
          FastAPI /ask

Data Flow

Zepto policy documents
        |
        v
      docs/
        |
        v
     ingest.py
        |
        +--> chunk documents
        |
        +--> all-MiniLM-L6-v2
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

File Responsibilities

ingest.py

Loads all eight policy documents from docs/, creates one chunk per document, generates embeddings using all-MiniLM-L6-v2, normalizes the embeddings, and stores the documents, embeddings, IDs, and metadata in the ChromaDB collection zepto_policies.

The ChromaDB collection is configured for cosine similarity so the query retrieves the top three most relevant policy chunks.

prompt.py

Contains the structured support-assistant prompt with:

Role

Context

Task

Format

Length

Negative constraint

Few-shot example

The prompt instructs the answer-generation component to use only the supplied policy context and not invent policy details.

graph.py

Contains the LangGraph workflow and the three required nodes:

classify_intent

retrieve_and_answer

direct_answer

classify_intent uses the required deterministic keyword heuristic in the default mock mode.

retrieve_and_answer embeds the query, retrieves the top three policy chunks from ChromaDB, and produces the answer from the retrieved context.

direct_answer provides the required fixed mock response for non-policy questions without retrieval.

The graph uses a conditional edge after intent classification.

models.py

Defines the Pydantic response schema:

answer: str
sources: list[str]
confidence: float

The confidence value is constrained to the range 0.0 to 1.0.

main.py

Creates the FastAPI application and exposes:

POST /ask

Request body:

{
  "query": "string"
}

The response is validated using the AnswerResponse Pydantic model.

Dockerfile

Builds the local application container, copies the policy corpus and application code, installs the required dependencies, runs ingest.py to build the ChromaDB index, and starts Uvicorn on port 7860.

Retrieval and Routing

The default graded behavior uses MOCK_LLM=1 or an unset MOCK_LLM.

Intent classification uses the deterministic keyword heuristic required by the capstone.

The policy keywords are:

delivery
return
refund
membership
tracking
cancel
gift card
support hours

Policy questions are routed to retrieve_and_answer.

General questions are routed to direct_answer.

For policy questions, retrieval always runs in both mock and optional real-LLM modes. The query is embedded and the top three chunks are retrieved from ChromaDB using cosine similarity.

Structured Prompt

The prompt in prompt.py is organized into the required sections:

ROLE
CONTEXT
TASK
FORMAT
LENGTH
NEGATIVE CONSTRAINT
FEW-SHOT EXAMPLE
CUSTOMER QUESTION

The negative constraint explicitly prevents invented policy details, and the few-shot example demonstrates the expected answer style.

MOCK_LLM Behavior

The graded baseline is fully deterministic and offline.

When:

MOCK_LLM=1

or the variable is not set:

intent classification uses the deterministic keyword heuristic

policy retrieval uses ChromaDB

the answer uses the retrieved top chunk

general questions use a fixed canned response

no external LLM API call is required

The policy retrieval mock response follows the format:

Based on the retrieved context: {top_chunk_snippet}

The general-question mock response is:

I can only answer questions about Zepto policies right now.

The mock confidence value is:

1.0

Optional Real-LLM Path

The application also contains an optional real-LLM path.

Set:

MOCK_LLM=0

and provide:

GROQ_API_KEY

The real path uses the Groq client and the model configured in graph.py.

Structured JSON is validated against the Pydantic response schema. If the real path returns invalid JSON or violates the response schema, the implementation retries up to two additional times before returning a clear error response.

The graded capstone baseline does not depend on this optional path.

Running Locally

From the support_assistant directory:

1. Build the local ChromaDB index

python ingest.py

Expected verification includes:

Documents loaded: 8
Chunks stored: 8
Collection: zepto_policies
ChromaDB collection count: 8
Task 1 verification: PASSED

2. Start the API

uvicorn main:app --reload --port 8000

The API is available at:

http://127.0.0.1:8000

API Usage

Endpoint:

POST /ask

Example 1: Policy Retrieval Query

Request:

{
  "query": "What is the delivery fee for an order below INR 149?"
}

Raw response from the local FastAPI test:

{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer\u0027s delivery zone and current order volume. Standard del","sources":["doc_01","doc_05","doc_07"],"confidence":1.0}

This query is classified as a policy question, performs ChromaDB retrieval, and returns retrieved document IDs in sources.

Example 2: General Query

Request:

{
  "query": "What is the capital of India?"
}

Raw response from the local FastAPI test:

{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}

This query is classified as a general question and does not perform policy retrieval.

Docker

Build the image from the support_assistant directory:

docker build -t zepto-support-assistant .

Run the container:

docker run --name zepto-support-assistant-container -p 7860:7860 zepto-support-assistant

The container starts Uvicorn on:

http://localhost:7860

The FastAPI endpoint remains:

POST /ask

The Docker build runs the ingestion step inside the image, so the ChromaDB index is recreated from the eight policy documents during the build.

Verification Summary

The implemented and locally tested baseline verified:

Task 1
  -> 8 documents loaded
  -> 8 chunks stored
  -> ChromaDB collection count = 8
  -> PASSED

Policy query
  -> policy_question
  -> ChromaDB retrieval
  -> top-3 sources returned
  -> confidence = 1.0

General query
  -> general_question
  -> no retrieval
  -> sources = []
  -> confidence = 1.0

FastAPI
  -> POST /ask tested for both policy and general queries

Docker
  -> image built successfully
  -> container served the FastAPI application on port 7860

Pipeline Summary

1. Load the 8 Zepto policy documents
2. Create one chunk per document
3. Generate all-MiniLM-L6-v2 embeddings
4. Store embeddings and metadata in ChromaDB
5. Receive a customer query through FastAPI
6. Classify the intent using LangGraph
7. Route policy questions to retrieval
8. Embed the query and retrieve the top 3 chunks using cosine similarity
9. Generate the deterministic mock answer from retrieved context
10. Validate the response with Pydantic
11. Return JSON through /ask