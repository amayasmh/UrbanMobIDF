# fichier: app/main.py

import streamlit as st

st.set_page_config(page_title="🚦 Mobilité Urbaine Optimisée", page_icon="🚦", layout="wide")

st.title("🚦 Bienvenue sur la plateforme de mobilité intelligente !")

st.markdown("""
Bienvenue dans votre application de gestion de la mobilité urbaine basée sur l'intelligence artificielle et les données ouvertes.

- 🔍 **Recherchez un itinéraire optimal entre deux arrêts.**
- 📈 **Analysez le trafic et les horaires en temps réel.**
- 📍 **Visualisez les données de transport sur une carte interactive.**
- 🚨 **Recevez des alertes et notifications sur les incidents.**

---

Utilisez le menu à gauche pour naviguer entre les différentes fonctionnalités ! 🚀
""")

st.image("https://images.axa-contento-118412.eu/www-axa-com%2Fce94839d-24c9-424c-8bed-1b520ef55386_fond-couv-mobility-nation-cover.jpg", caption="Gestion intelligente de la mobilité", use_container_width=True)
