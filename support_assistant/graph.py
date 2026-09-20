import json
import os
from pathlib import Path
from typing import TypedDict

from groq import Groq
from langgraph.graph import StateGraph, END
from pydantic import ValidationError
from sentence_transformers import SentenceTransformer
import chromadb

from models import AnswerResponse
from prompt import PROMPT_TEMPLATE

class GraphState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_chunks: list[str]
    retrieved_ids: list[str]
    answer: str
    sources: list[str]
    confidence: float
    
MOCK_LLM = os.getenv("MOCK_LLM", "1")

groq_client = None

if MOCK_LLM == "0":
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise RuntimeError(
            "MOCK_LLM=0 requires the GROQ_API_KEY environment variable."
        )

    groq_client = Groq(api_key=groq_api_key)


def call_real_llm(
    system_prompt: str,
    user_prompt: str,
) -> AnswerResponse:
    """
    Optional real-LLM path.

    The capstone requires up to 3 total attempts:
    1 initial attempt + 2 corrective retries.
    """

    last_error = None

    for attempt in range(3):
        corrective_instruction = ""

        if attempt > 0:
            corrective_instruction = (
                "\n\nYour previous response failed validation. "
                "Return ONLY valid JSON matching exactly this schema:\n"
                '{"answer": "string", "sources": ["string"], "confidence": 0.0}'
            )

        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt + corrective_instruction,
                    },
                ],
                response_format={"type": "json_object"},
            )

            raw_content = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_content)

            return AnswerResponse.model_validate(parsed)

        except (json.JSONDecodeError, ValidationError, Exception) as exc:
            last_error = exc

    return AnswerResponse(
        answer=f"ERROR: Unable to produce a valid response after 3 attempts: {last_error}",
        sources=[],
        confidence=0.0,
    )
    
def classify_intent(state: GraphState) -> GraphState:
    query = state["query"].strip()

    # Required graded baseline:
    # MOCK_LLM unset or set to "1" -> keyword heuristic, no LLM call.
    if MOCK_LLM != "0":
        query_lower = query.lower()

        policy_keywords = [
            "delivery",
            "return",
            "refund",
            "membership",
            "tracking",
            "cancel",
            "gift card",
            "support hours",
        ]

        if any(keyword in query_lower for keyword in policy_keywords):
            intent = "policy_question"
        else:
            intent = "general_question"

        return {
            **state,
            "intent": intent,
        }

    # Optional real-LLM path:
    # MOCK_LLM=0 -> classify using the configured LLM.
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You classify Zepto customer questions. "
                    "Return JSON with exactly one field: intent. "
                    "intent must be either policy_question or general_question. "
                    "Use policy_question when the question needs Zepto policy "
                    "information and general_question otherwise."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content or "{}"

    try:
        parsed = json.loads(raw_content)
        intent = parsed.get("intent")

        if intent not in {"policy_question", "general_question"}:
            raise ValueError("Invalid intent returned by the LLM.")

    except (json.JSONDecodeError, ValueError):
        intent = "general_question"

    return {
        **state,
        "intent": intent,
    }
    

# Connect to the ChromaDB index created by ingest.py
BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection("zepto_policies")

# Same embedding model used during ingestion.
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_and_answer(state: GraphState) -> GraphState:
    query = state["query"]

    # Retrieval always runs in both MOCK_LLM modes.
    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    retrieved_chunks = results["documents"][0]
    retrieved_ids = results["ids"][0]

    # Required graded baseline.
    if MOCK_LLM != "0":
        snippet = retrieved_chunks[0][:200]

        return {
            **state,
            "retrieved_chunks": retrieved_chunks,
            "retrieved_ids": retrieved_ids,
            "answer": f"Based on the retrieved context: {snippet}",
            "sources": retrieved_ids,
            "confidence": 1.0,
        }

    # Optional real-LLM generation path.
    context = "\n\n".join(
        f"[{doc_id}]\n{chunk}"
        for doc_id, chunk in zip(retrieved_ids, retrieved_chunks)
    )

    user_prompt = PROMPT_TEMPLATE.format(
        context=context,
        query=query,
    )

    real_response = call_real_llm(
        system_prompt=(
            "You are the Zepto support assistant. "
            "Use only the supplied policy context."
        ),
        user_prompt=user_prompt,
    )

    return {
        **state,
        "retrieved_chunks": retrieved_chunks,
        "retrieved_ids": retrieved_ids,
        "answer": real_response.answer,
        "sources": real_response.sources,
        "confidence": real_response.confidence,
    }
    
def direct_answer(state: GraphState) -> GraphState:
    query = state["query"]

    # Required graded baseline.
    if MOCK_LLM != "0":
        return {
            **state,
            "answer": "I can only answer questions about Zepto policies right now.",
            "sources": [],
            "confidence": 1.0,
        }

    # Optional real-LLM path.
    real_response = call_real_llm(
        system_prompt=(
            "You are a Zepto customer support assistant. "
            "Answer the customer's question directly. "
            "Return a valid JSON response containing answer, sources, "
            "and confidence."
        ),
        user_prompt=query,
    )

    return {
        **state,
        "answer": real_response.answer,
        "sources": real_response.sources,
        "confidence": real_response.confidence,
    }
    

def route_after_classification(state: GraphState) -> str:
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# Build the LangGraph StateGraph
graph_builder = StateGraph(GraphState)

graph_builder.add_node("classify_intent", classify_intent)
graph_builder.add_node("retrieve_and_answer", retrieve_and_answer)
graph_builder.add_node("direct_answer", direct_answer)

graph_builder.set_entry_point("classify_intent")

graph_builder.add_conditional_edges(
    "classify_intent",
    route_after_classification,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)

graph_builder.add_edge("retrieve_and_answer", END)
graph_builder.add_edge("direct_answer", END)

graph = graph_builder.compile()

def build_response(state: GraphState) -> AnswerResponse:
    return AnswerResponse(
        answer=state.get("answer", ""),
        sources=state.get("sources", state.get("retrieved_ids", [])),
        confidence=state.get("confidence", 1.0),
    )