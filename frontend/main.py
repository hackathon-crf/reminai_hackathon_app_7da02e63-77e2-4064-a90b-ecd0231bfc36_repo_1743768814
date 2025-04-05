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
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
# :clé_anglaise: Pour résoudre les imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import random
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from backend.utils import generate_questions_by_level, save_dashboard_results
# ----------- 🌈 STYLE -----------
def main():
    st.set_page_config(page_title="Croix-Rouge IA", page_icon="🚑", layout="wide")
    st.markdown("""
        <style>
            body {
                background: linear-gradient(to right, #F8F9FA, #E0EAFC);
            }
            .block-container {
                max-width: 1000px;
                margin: auto;
            }
            h1, h2, h3 {
                font-family: 'Segoe UI', sans-serif;
            }
            .stButton>button {
                background-color: #E74C3C;
                color: white;
                border-radius: 8px;
                padding: 0.6em 2em;
                font-size: 17px;
                border: none;
            }
            .stButton>button:hover {
                background-color: #C0392B;
            }
            .correct {
                background-color: #D4EDDA;
                border-left: 6px solid #28A745;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 10px;
            }
            .wrong {
                background-color: #F8D7DA;
                border-left: 6px solid #DC3545;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)
    # ----------- 🔄 TABS -----------
    tab1, tab2 = st.tabs(["Quiz", "📊 Dashboard"])
    # ---------------------- 🎯 TAB 1 : QUIZ ---------------------- #
    with tab1:
        st.title("🚑 Quiz interactif Croix-Rouge")
        st.markdown("### 🎯  Apprends les gestes de premiers secours avec l'IA Mistral")
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
    # ---------------------- 📊 TAB 2 : DASHBOARD ---------------------- #
    with tab2:
        st.title("📊 Tableau de bord interactif des résultats")
        if os.path.exists("dashboard_results.json"):
            with open("dashboard_results.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            clean_data = []
            for entry in data:
                if "timestamp" in entry:
                    clean_data.append({
                        "timestamp": entry["timestamp"],
                        "niveau": entry["level"],
                        "score": entry["score"],
                        "total": entry["total"]
                    })
            df = pd.DataFrame(clean_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.subheader("📈 Évolution des scores dans le temps")
            col1, col2 = st.columns([3, 1])
            with col1:
                fig = px.line(
                    df,
                    x="timestamp",
                    y="score",
                    color="niveau",
                    title="Progression des performances",
                    markers=True,
                    line_shape="spline",
                    labels={"timestamp": "Date", "score": "Score"},
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.metric("📊 Total de Quiz", len(df))
                st.metric("🎯 Score moyen", f"{df['score'].mean():.2f}")
            st.subheader("📑 Historique détaillé des sessions")
            for session in reversed(data):
                st.markdown("----")
                st.markdown(f"### 🧠 Niveau : {session['level']} | 📅 {session['timestamp']}")
                st.write(f"✅ Score : **{session['score']} / {session['total']}**")
                with st.expander("📋 Voir les réponses détaillées"):
                    for r in session["answers"]:
                        st.markdown(f"- **Q**: {r['question']}")
                        st.markdown(f"  - ✅ Réponse correcte : `{r['correct_answer']}`")
                        st.markdown(f"  - 🧠 Ta réponse : `{r['user_answer']}`")
        else:
            st.warning("🚨 Aucun résultat enregistré pour le moment.")