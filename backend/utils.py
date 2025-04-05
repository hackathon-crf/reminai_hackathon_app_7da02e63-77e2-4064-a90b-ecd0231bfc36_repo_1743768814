"""
Utilities module for the Questions Mentor backend.

This module provides various utility functions for:
- PDF text extraction
- Text chunking
- Quiz generation using Mistral AI
- RAG (Retrieval-Augmented Generation) search functionality
- Question parsing and formatting
- Score tracking and persistence

The module integrates with external services and models including:
- Mistral AI API for question generation
- SentenceTransformer for text embeddings
- FAISS for similarity search
- PyMuPDF for PDF processing
"""

import os
import json
import datetime
from typing import List, Dict, Any, Union
import fitz  # PyMuPDF
import requests
import faiss
import pickle
import numpy as np
import re
import random
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Chargement .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Embedding
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Lire PDF ---
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Concatenated text content from all pages of the PDF
    """
    doc = fitz.open(pdf_path)
    return "".join(page.get_text() for page in doc)

# --- Chunk ---
def chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    """
    Split text into chunks of specified maximum length.

    Args:
        text (str): The text to be chunked
        max_chars (int, optional): Maximum characters per chunk. Defaults to 1200.

    Returns:
        List[str]: List of text chunks
    """
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# --- Générer un quiz avec IA ---
def generate_quiz(prompt: str) -> str:
    """
    Generate quiz content using Mistral AI API.

    Args:
        prompt (str): The prompt containing instructions for quiz generation

    Returns:
        str: Generated quiz content from the AI model

    Raises:
        requests.exceptions.RequestException: If API call fails
    """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# --- Charger index et chunks ---
index_path = os.path.join("backend", "rag_index.pkl")
chunks_path = os.path.join("backend", "rag_chunks.pkl")
faiss_index = faiss.read_index(index_path)
with open(chunks_path, "rb") as f:
    chunks_data = pickle.load(f)

# --- Recherche RAG ---
def search_similar_chunks(query: str, top_k: int = 3) -> List[str]:
    """
    Search for similar text chunks using FAISS similarity search.

    Args:
        query (str): The search query
        top_k (int, optional): Number of similar chunks to return. Defaults to 3.

    Returns:
        List[str]: List of most similar text chunks
    """
    embedding = embedding_model.encode([query])
    distances, indices = faiss_index.search(np.array(embedding), top_k)
    return [chunks_data[i] for i in indices[0]]

# --- Parsing IA ---
def parse_question(raw: str) -> Dict[str, Any]:
    """
    Parse raw quiz content into structured question format.

    Args:
        raw (str): Raw question text from AI generation

    Returns:
        Dict[str, Any]: Structured question data containing:
            - question: The main question text
            - choices: List of multiple choice options
            - answer: The correct answer text
    """
    lines = raw.split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    question = next((l for l in lines if "?" in l), lines[0])
    choices = [l for l in lines if l.startswith(("A)", "B)", "C)", "D)"))]

    correct_line = next((l for l in lines if "Bonne réponse" in l or "Réponse" in l), "")
    match = re.search(r"([A-D]\))\s*(.+)", correct_line)

    correct_full = ""
    if match:
        label = match.group(1)  # ex: B)
        correct_full = next((c for c in choices if c.startswith(label)), "")

    return {
        "question": question,
        "choices": choices,
        "answer": correct_full
    }

# --- Générer questions ---
def generate_questions_by_level(level: str, max_questions: int = 3) -> List[Dict[str, Any]]:
    """
    Generate multiple questions for a specific difficulty level.

    Args:
        level (str): Difficulty level ('Débutant', 'Intermédiaire', or 'Expert')
        max_questions (int, optional): Number of questions to generate. Defaults to 3.

    Returns:
        List[Dict[str, Any]]: List of generated questions in structured format

    Note:
        Questions are generated using RAG context from various first aid themes
    """
    instructions = {
        "Débutant": "- 1 QCM niveau débutant avec 4 choix dont UNE seule bonne réponse.",
        "Intermédiaire": "- 1 situation réelle où il faut faire un choix (niveau intermédiaire).",
        "Expert": "- 1 cas complexe pour niveau expert avec plusieurs étapes à résoudre."
    }

    themes = [
        "hémorragie", "obstruction", "malaise", "arrêt cardiaque", "brûlure", "traumatisme",
        "intoxication", "noyade", "électrocution", "violence", "incendie", "urgence scolaire"
    ]

    questions = []
    for _ in range(max_questions):
        topic = random.choice(themes)
        query = f"Crée une question niveau {level} sur les gestes de secours liés à {topic}"
        context = "\n".join(search_similar_chunks(query, top_k=5))
        prompt = f"""
        Tu es un formateur expert de la Croix-Rouge française, spécialisé en premiers secours.

        Ta mission est de créer une question d’évaluation claire et précise sur les gestes de secours.

        Voici les consignes à suivre :
        - Thème : {topic}
        - Niveau : {level}
        - Formule UNE question QCM avec 4 choix A) B) C) D).
        - Une seule bonne réponse.
        - Les autres propositions doivent être plausibles.
        - Termine par : Bonne réponse : X) Texte complet

        Contexte d’appui :
        {context}
        """
        raw = generate_quiz(prompt)
        parsed = parse_question(raw)
        questions.append(parsed)

    return questions

# --- Sauvegarde des scores ---
def save_dashboard_results(level: str, score: int, total: int, answers: List[Dict[str, Any]]) -> None:
    """
    Save quiz results to a JSON file for dashboard tracking.

    Args:
        level (str): Difficulty level of the quiz
        score (int): Number of correct answers
        total (int): Total number of questions
        answers (List[Dict[str, Any]]): Detailed answer data for each question

    Note:
        Results are appended to 'dashboard_results.json' with timestamps
    """
    result = {
        "level": level,
        "score": score,
        "total": total,
        "answers": answers,
        "timestamp": datetime.datetime.now().isoformat()
    }
    path = "dashboard_results.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(result)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
