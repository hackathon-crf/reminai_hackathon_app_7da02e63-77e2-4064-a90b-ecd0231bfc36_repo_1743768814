"""
Quiz Generator Service Module for the Questions Mentor backend.

This module provides functionality to generate quizzes using the Mistral AI model.
It creates three types of questions:
- A beginner-level multiple choice question
- An intermediate-level situational question
- An expert-level complex case scenario

The module interacts with the RAG API to generate contextually relevant questions
based on provided text content.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
RAG_API_BASE_URL = "https://hackathon-ia-et-crise.fr"

def generate_quiz_from_text(section_text: str) -> dict:
    """
    Generate a multi-level quiz from provided text using the Mistral AI model.

    This function creates a quiz containing three different types of questions:
    1. A beginner-level MCQ with 4 choices and one correct answer
    2. An intermediate-level real-world situation requiring decision making
    3. An expert-level complex case scenario

    Args:
        section_text (str): The text content from which to generate the quiz

    Returns:
        dict: JSON response containing the generated quiz questions and answers.
              In case of error, returns a dict with an 'error' key.

    Raises:
        Exception: If there's an error during the API call, the error is caught
                  and returned in the response dictionary.

    Note:
        Requires MISTRAL_API_KEY environment variable to be set for authentication
    """
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
