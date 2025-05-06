# fichier : app/utils.py

import streamlit as st

# Clé pour stocker la page active dans la session
SESSION_PAGE_KEY = "current_page"

def get_current_page():
    """
    Récupère la page active depuis la session utilisateur.
    Si aucune page n'est définie, retourne 'home' par défaut.
    """
    return st.session_state.get(SESSION_PAGE_KEY, "home")

def set_current_page(page_name):
    """
    Définit la page active dans la session utilisateur.
    """
    st.session_state[SESSION_PAGE_KEY] = page_name
