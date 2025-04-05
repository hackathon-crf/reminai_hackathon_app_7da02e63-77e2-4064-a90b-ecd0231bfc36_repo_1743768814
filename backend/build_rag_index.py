"""
RAG Index Builder module for the Questions Mentor system.

This module handles the creation of the FAISS search index used by the RAG system:
- Extracts text from PDF documentation
- Splits text into manageable chunks
- Generates embeddings using SentenceTransformer
- Creates and saves a FAISS index for similarity search
- Persists text chunks for later retrieval

The index enables efficient semantic search across first aid documentation,
which is used to generate contextually relevant quiz questions.
"""

import os
import pickle
from typing import List
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file to process

    Returns:
        str: Concatenated text content from all pages of the PDF
    """
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """
    Split text into chunks of specified maximum length.

    Args:
        text (str): The text to be chunked
        max_chars (int, optional): Maximum characters per chunk. Defaults to 1000.

    Returns:
        List[str]: List of text chunks
    """
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def build_index() -> None:
    """
    Build and save the FAISS search index and text chunks.

    This function:
    1. Reads the PDF documentation
    2. Splits it into chunks
    3. Generates embeddings for each chunk
    4. Creates a FAISS L2 index from the embeddings
    5. Saves both the index and original chunks to disk

    The resulting files (rag_index.pkl and rag_chunks.pkl) are used by
    the RAG system to find relevant context for quiz generation.
    """
    pdf_path = os.path.join("backend", "data.pdf")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)

    # Embedding des chunks
    embeddings = embedding_model.encode(chunks)

    # Création de l’index FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    # Sauvegarder l’index FAISS
    faiss.write_index(index, os.path.join("backend", "rag_index.pkl"))

    # Sauvegarder les chunks pour pouvoir y accéder plus tard
    with open(os.path.join("backend", "rag_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"✅ RAG index construit avec {len(chunks)} morceaux.")

# Lancer
if __name__ == "__main__":
    build_index()
