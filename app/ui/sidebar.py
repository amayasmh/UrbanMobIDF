import streamlit as st
from PIL import Image
import app.config as config
from app.utils import get_current_page, set_current_page
from app.screens import screens

def render_sidebar():
    st.sidebar.title("🚦 Mobilité Urbaine Optimisée")

    # Logo
    try:
        image = Image.open("app/assets/logo.png")
        st.sidebar.image(image, use_container_width=True)
    except Exception:
        st.sidebar.warning("⚠️ Logo introuvable : assets/logo.png")

    # Intro
    st.sidebar.markdown("""
        Bienvenue dans votre application de **gestion de la mobilité urbaine** basée sur **l'intelligence artificielle** et **les données ouvertes**.

        **Fonctionnalités principales :**
        - 🔍 *Recherche d’itinéraire optimal entre deux arrêts*
        - 📈 *Analyses des flux et prévisions de trafic*
        - 🗺️ *Visualisation sur carte interactive*
        - 🚨 *Alertes incidents en temps réel*
    """)

    # CSS uniforme pour les boutons
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            border: 1px solid #ccc;
            padding: 0.4rem 0.75rem;
            margin-bottom: 0.4rem;
            border-radius: 6px;
            text-align: left;
            background-color: #f4f4f4;
        }
        .stButton > button:hover {
            background-color: #e0e0e0;
        }
        .selected {
            background-color: #cfe2ff !important;
            border: 2px solid #0056b3 !important;
            font-weight: bold;
            color: #003580 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Menu")

    current = get_current_page()

    # Création de boutons unifiés
    for page in screens:
        btn_label = f"{page['icon']} {page['title']}" if "icon" in page else page['title']
        if page["name"] == current:
            # Ajoute une classe via HTML pour bouton sélectionné
            st.markdown(f'<div class="stButton"><button class="selected">{btn_label}</button></div>', unsafe_allow_html=True)
        else:
            if st.sidebar.button(btn_label, key=page["name"]):
                set_current_page(page["name"])
                st.rerun()

    # Contact
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Contact")
    st.sidebar.markdown("""
        Pour toute question ou suggestion, n'hésitez pas à nous contacter :

        - 📧 Email : [aghiles.saghir@supdevinci-edu.fr](mailto:aghiles.saghir@supdevinci-edu.fr)
        - 📞 Téléphone : +33 6 12 34 56 78
    """)

    # Infos
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Version : `{config.VERSION}`")
    st.sidebar.markdown("### Crédits")
    st.sidebar.markdown("""
        - Développé par : [S.Aghiles, M.Amayas]  
        - Licence : Sup de Vinci
    """)
