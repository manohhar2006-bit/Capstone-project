from fastapi import FastAPI
from pydantic import BaseModel

from graph import graph, build_response
from models import AnswerResponse


app = FastAPI(title="Zepto Support Assistant")


class AskRequest(BaseModel):
    query: str


@app.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest) -> AnswerResponse:
    state = graph.invoke({"query": request.query})
    return build_response(state)