import streamlit as st
import os
import sys

# ➤ Ajout du chemin absolu du dossier parent
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

from database import login_user, register_user

st.set_page_config(page_title="Login Croix-Rouge", page_icon="🔐")

menu = st.sidebar.selectbox("Menu", ["Se connecter", "S'inscrire"])

if menu == "S'inscrire":
    st.title("📝 Création de compte")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    fullname = st.text_input("Nom complet")
    email = st.text_input("Email")
    role = st.selectbox("Rôle", ["grand_public", "secouriste", "formateur"])

    if st.button("Créer le compte"):
        if register_user(username, password, role, fullname, email):
            st.success("✅ Compte créé avec succès ! Connectez-vous.")
        else:
            st.error("❌ Ce nom d'utilisateur existe déjà.")

if menu == "Se connecter":
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        role = login_user(username, password)
        if role:
            st.success(f"Bienvenue {username} !")

            if role == "formateur":
                st.markdown("🎯 Redirection vers le **tableau de bord des résultats**...")
                st.markdown("**→ Ouvre le fichier : `frontend/dashboard.py`**")

            else:
                st.markdown("🚀 Redirection vers le **quiz interactif**...")
                st.markdown("**→ Ouvre le fichier : `frontend/main.py`**")
        else:
            st.error("⚠️ Identifiants incorrects.")
