from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

# ChromaDB persistent client
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Recreate the collection so that running the script again
# produces a clean deterministic index.
try:
    client.delete_collection("zepto_policies")
except Exception:
    pass

collection = client.create_collection(
    name="zepto_policies",
    metadata={
        "description": "Zepto policy document embeddings",
        "hnsw:space": "cosine"
    }
)

# Load the required open-source embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

documents = []
ids = []
metadatas = []

# Load all 8 required policy documents.
# Each document is kept as one chunk because the supplied
# policy documents are short and the capstone explicitly allows
# simple per-document chunking.
for doc_path in sorted(DOCS_DIR.glob("doc_*.txt")):
    text = doc_path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Empty document found: {doc_path.name}")

    documents.append(text)
    ids.append(doc_path.stem)
    metadatas.append(
        {
            "document_id": doc_path.stem,
            "source": doc_path.name,
        }
    )

if len(documents) != 8:
    raise ValueError(
        f"Expected 8 policy documents, but found {len(documents)}."
    )

# Generate local embeddings
embeddings = model.encode(
    documents,
    normalize_embeddings=True
).tolist()

# Store documents, embeddings, IDs, and metadata in ChromaDB
collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
)

print("Ingestion completed successfully.")
print(f"Documents loaded: {len(documents)}")
print(f"Chunks stored: {len(documents)}")
print(f"Collection: {collection.name}")
print(f"ChromaDB path: {CHROMA_DIR}")
print(f"Embedding model: all-MiniLM-L6-v2")

# Verification
count = collection.count()
print(f"ChromaDB collection count: {count}")

if count != 8:
    raise RuntimeError(
        f"Expected 8 stored chunks, but ChromaDB contains {count}."
    )

print("Task 1 verification: PASSED")