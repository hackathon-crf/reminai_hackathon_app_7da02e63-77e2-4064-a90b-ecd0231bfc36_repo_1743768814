"""
PDF Quiz Generator using Mistral AI

This module provides functionality to generate quizzes from PDF documents using the Mistral AI API.
It extracts text from PDFs, splits it into manageable chunks, and uses Mistral AI to generate
three types of questions:
- A beginner-level MCQ
- An intermediate-level real-world situation
- An expert-level complex case

Requirements:
    - PyMuPDF (fitz)
    - requests
    - python-dotenv
    - Mistral AI API key in .env file

Example:
    from pdf_to_quiz_mistral import generate_quiz_from_pdf
    generate_quiz_from_pdf("path/to/your/document.pdf")
"""

import os
from typing import List, Dict
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv

# Load environment variables and configure API
load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in environment variables")

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def extract_text(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text content from all pages

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        fitz.FileDataError: If file is not a valid PDF
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text(text: str, max_len: int = 1500) -> List[str]:
    """
    Split text into smaller chunks of maximum length while preserving paragraph breaks.

    Args:
        text (str): Input text to split
        max_len (int, optional): Maximum length of each chunk. Defaults to 1500.

    Returns:
        List[str]: List of text chunks, each no longer than max_len
    """
    chunks = []
    while len(text) > max_len:
        idx = text[:max_len].rfind("\n")
        if idx == -1:
            idx = max_len
        chunks.append(text[:idx].strip())
        text = text[idx:]
    chunks.append(text.strip())
    return chunks

def call_mistral(prompt: str) -> str:
    """
    Make an API call to Mistral AI to generate quiz content.

    Args:
        prompt (str): The prompt to send to Mistral AI

    Returns:
        str: Generated response from Mistral AI

    Raises:
        requests.exceptions.RequestException: If API call fails
        KeyError: If response format is unexpected
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=body)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_quiz_from_pdf(pdf_path: str) -> None:
    """
    Generate a quiz from a PDF document using Mistral AI.
    
    This function:
    1. Extracts text from the PDF
    2. Splits it into manageable chunks
    3. For each chunk, generates:
       - A beginner-level MCQ
       - An intermediate-level situation
       - An expert-level complex case

    Args:
        pdf_path (str): Path to the PDF file to process

    Note:
        Currently configured to process only the first chunk for testing purposes.
        Remove the slice and break statement for full processing.
    """
    text = extract_text(pdf_path)
    chunks = split_text(text)
    print("🧩 Nombre de morceaux extraits :", len(chunks))

    for i, chunk in enumerate(chunks[:1]):  # ← pour test : on prend juste 1 morceau
        prompt = f"""
Tu es un expert en formation Croix-Rouge. Lis ce texte et génère :
- 1 QCM niveau débutant avec 4 choix (1 bonne réponse)
- 1 situation réelle intermédiaire
- 1 cas complexe pour niveau expert

Texte : {chunk}
"""
        print(f"\n📦 Génération du quiz pour le Chunk {i+1}...")
        result = call_mistral(prompt)
        print(result)
        break  # ← on arrête après un test

if __name__ == "__main__":
    generate_quiz_from_pdf("backend/data.pdf")
