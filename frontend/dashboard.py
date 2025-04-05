# frontend/dashboard.py
import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Quiz", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord interactif des résultats")

# Lecture des résultats
if os.path.exists("dashboard_results.json"):
    with open("dashboard_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Nettoyage et transformation en DataFrame
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

    # --- Affichage du graphique d'évolution ---
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

    # --- Détail des sessions ---
    st.subheader("🗂️ Historique détaillé des sessions")

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
