"""
Frontend Streamlit application for the Questions Mentor quiz system.

This module implements an interactive quiz interface using Streamlit, featuring:
- Three difficulty levels (Beginner, Intermediate, Expert)
- AI-generated questions using Mistral AI
- Real-time scoring and feedback
- Quiz result persistence
- Custom styling and user interface elements

The application integrates with the backend RAG system to generate
contextually relevant questions about first aid procedures.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"  # Fix for Intel MKL library conflicts

# Add parent directory to Python path for imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from backend.utils import generate_questions_by_level, save_dashboard_results
import random

def main():

    # ----------- 🌈 STYLE PERSONNALISÉ (CSS) -----------
    st.set_page_config(page_title="Quiz Croix-Rouge", page_icon="🚑")

    st.markdown("""
        <style>
            body {
                background: linear-gradient(to right, #f8f9fa, #e0eafc);
            }
            .block-container {
                max-width: 850px;
                margin: auto;
            }
            h1, h2, h3 {
                font-family: 'Segoe UI', sans-serif;
            }
            h1 {
                font-size: 2.8em;
                color: #2c3e50;
            }
            h2 {
                color: #e74c3c;
            }
            .stButton>button {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 0.6em 2em;
                font-size: 17px;
                border: none;
            }
            .stButton>button:hover {
                background-color: #c0392b;
            }
            .correct {
                background-color: #d4edda;
                border-left: 6px solid #28a745;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 10px;
            }
            .wrong {
                background-color: #f8d7da;
                border-left: 6px solid #dc3545;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # ----------- 🧠 EN-TÊTE -----------
    st.title("🚑 Quiz interactif Croix-Rouge")
    st.markdown("### Apprends les gestes de premiers secours avec l’IA Mistral")

    # ----------- 📘 CHOIX DU NIVEAU -----------
    niveau = st.radio("Sélectionne ton niveau :", ["Débutant", "Intermédiaire", "Expert"])

    if st.button("🎯 Lancer le Quiz"):
        with st.spinner("📚 Génération des questions IA..."):
            questions = generate_questions_by_level(niveau)

        st.session_state["questions"] = questions
        st.session_state["niveau"] = niveau
        st.session_state["reponses"] = []
        st.session_state["score"] = 0
        st.session_state["index"] = 0
        st.rerun()

    # ----------- 🧩 AFFICHAGE DES QUESTIONS -----------
    if "questions" in st.session_state and st.session_state["index"] < len(st.session_state["questions"]):
        q = st.session_state["questions"][st.session_state["index"]]
        st.markdown(f"### Question {st.session_state['index']+1} : {q['question']}")
        choix = st.radio("Ta réponse :", q["choices"], key=st.session_state["index"])

        if st.button("Valider ma réponse"):
            bonne_reponse = q["answer"]
            user_reponse = choix

            if user_reponse.strip().lower() == bonne_reponse.strip().lower():
                st.success("✅ Bonne réponse !")
                st.session_state["score"] += 1
            else:
                st.error(f"❌ Mauvaise réponse. La bonne était : {bonne_reponse}")

            st.session_state["reponses"].append({
                "question": q["question"],
                "choices": q["choices"],
                "user_answer": user_reponse,
                "correct_answer": bonne_reponse
            })

            st.session_state["index"] += 1
            st.rerun()

    # ----------- 🎉 FIN DU QUIZ -----------
    elif "questions" in st.session_state and st.session_state["index"] >= len(st.session_state["questions"]):
        score = st.session_state["score"]
        total = len(st.session_state["questions"])

        st.balloons()
        st.success(f"🎉 Bravo ! Tu as terminé le quiz. Score : **{score} / {total}**")

        save_dashboard_results(st.session_state["niveau"], score, total, st.session_state["reponses"])

        st.markdown("### 📋 Résumé de tes réponses :")
        for r in st.session_state["reponses"]:
            is_correct = r['user_answer'].strip().lower() == r['correct_answer'].strip().lower()
            classe = "correct" if is_correct else "wrong"
            st.markdown(f"""
            <div class="{classe}">
            <strong>Q:</strong> {r['question']}<br>
            ✅ Réponse correcte : {r['correct_answer']}<br>
            {"🔴 Ta réponse : " + r['user_answer'] if not is_correct else ""}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔁 Rejouer"):
            for k in ["questions", "niveau", "reponses", "score", "index"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
