from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services import query_rag

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/api/ask")  # <-- POST, c'est crucial
def ask_question(req: QuestionRequest):
    return query_rag(req.question)
