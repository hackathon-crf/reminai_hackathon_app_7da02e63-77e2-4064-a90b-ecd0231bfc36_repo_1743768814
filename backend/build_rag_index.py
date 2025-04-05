# backend/build_rag_index.py
import os
import pickle
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Charger le modèle d'embedding
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Lire le texte du PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

# Diviser le texte en morceaux
def chunk_text(text, max_chars=1000):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# Construire l'index RAG
def build_index():
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
