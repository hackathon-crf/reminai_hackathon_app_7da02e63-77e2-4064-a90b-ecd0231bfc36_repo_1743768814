"""
API routes module for the Questions Mentor backend.

This module defines the API endpoints and request/response models for the application.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services import query_rag

router = APIRouter()

class QuestionRequest(BaseModel):
    """
    Request model for question submission.

    Attributes:
        question (str): The question text to be processed by the RAG system
    """
    question: str

@router.post("/api/ask")
async def ask_question(req: QuestionRequest):
    """
    Process a question using the RAG (Retrieval-Augmented Generation) system.

    Args:
        req (QuestionRequest): The request object containing the question

    Returns:
        dict: The RAG system's response containing relevant information
    """
    return query_rag(req.question)
