FROM python:3.11-slim

WORKDIR /app

COPY docs ./docs
COPY ingest.py .
COPY prompt.py .
COPY graph.py .
COPY models.py .
COPY main.py .

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    langgraph \
    chromadb \
    sentence-transformers

RUN python ingest.py

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]