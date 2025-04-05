import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
RAG_API_BASE_URL = "https://hackathon-ia-et-crise.fr"

def generate_quiz_from_text(section_text):
    prompt_template = """
Tu es un expert en formation Croix-Rouge. À partir du texte suivant, génère :
- 1 QCM niveau débutant avec 4 choix dont UNE seule bonne réponse.
- 1 situation réelle (niveau intermédiaire) où il faut faire un choix.
- 1 cas complexe pour niveau expert.

Texte : {context}

Question : Créer un quiz

Réponse :
"""

    prompt = prompt_template.replace("{context}", section_text)

    json_data = {
        "query": "Créer un quiz",
        "model_family": "mistral",
        "model_name": "mistral-small-latest",
        "api_key": API_KEY,
        "prompt": prompt,
        "collection_name": "secourisme",
        "history_data": "[]"
    }

    url = f"{RAG_API_BASE_URL}/api/app/inferencing/retrieve_answer_using_collections"

    try:
        # ✅ ENVOI des données dans le CORPS en JSON (pas en query string)
        response = requests.post(url, json=json_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Erreur lors de l'appel au RAG :", e)
        return {"error": str(e)}
