import requests
import os
from dotenv import load_dotenv

load_dotenv()

def query_rag(question: str):
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
