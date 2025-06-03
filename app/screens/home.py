# fichier : app/screens/accueil.py

import streamlit as st


def run():
    st.title("🏙️ Accueil - Optimisation de la Mobilité Urbaine")

    st.markdown("""
    Bienvenue dans l'application d'optimisation de la mobilité urbaine. 
    Naviguez à travers les différents onglets pour explorer les fonctionnalités disponibles.
    """)

    st.markdown("""
    ### 🌦️ Prévisions Météo Paris
    """)

    st.components.v1.html(
        '<iframe src="https://www.meteo-villes.com/widget/prevision-meteo?type=expertized&amp;city=2&amp;wgt=full&amp;days=5&amp;bg-clr=ffffff&amp;ft-clr=475dff" frameborder="0" style="width: 340px; height: 375px;"></iframe>',
        height=400,
        scrolling=False
    )