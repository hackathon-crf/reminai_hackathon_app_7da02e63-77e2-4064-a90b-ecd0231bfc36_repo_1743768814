import os
import fitz
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text(text, max_len=1500):
    chunks = []
    while len(text) > max_len:
        idx = text[:max_len].rfind("\n")
        if idx == -1:
            idx = max_len
        chunks.append(text[:idx].strip())
        text = text[idx:]
    chunks.append(text.strip())
    return chunks

def call_mistral(prompt):
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

def generate_quiz_from_pdf(pdf_path):
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
