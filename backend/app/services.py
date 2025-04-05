"""
Services module for the Questions Mentor backend.

This module handles the interaction with the RAG (Retrieval-Augmented Generation) system
through external API calls. It manages authentication and request handling for the RAG service.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def query_rag(question: str) -> dict:
    """
    Query the RAG system with a user question.

    This function sends the question to an external RAG API endpoint and retrieves
    relevant information based on the question context.

    Args:
        question (str): The user's question to be processed

    Returns:
        dict: JSON response from the RAG system containing the answer and relevant context

    Note:
        Requires MISTRAL_API_KEY environment variable to be set for authentication
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    url = "https://hackathon-ia-et-crise.fr/reminai/chatbot/api/app/back_app/"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "query": question,
        "collection": "secourisme"  # ← adapte si besoin
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()
