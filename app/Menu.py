# fichier : app/Menu.py

import os
import sys

import streamlit as st

# Ajouter le chemin racine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Définir la config AVANT tout Streamlit
st.set_page_config(page_title="🚦 Mobilité Urbaine Optimisée", page_icon="🚦", layout="wide")

from app.screens import screens
from app.ui.sidebar import render_sidebar
from app.utils import get_current_page

# Rendu de la sidebar
render_sidebar()

# Récupérer la page courante
current = get_current_page()

# Routing dynamique
try:
    page_module = __import__(f"app.screens.{current}", fromlist=["run"])
    page_module.run()
except ModuleNotFoundError:
    st.error(f"❌ Page introuvable : `{current}`")
except AttributeError:
    st.warning(f"⚠️ La page `{current}` ne contient pas de fonction `run()`.")

# Vérifie la base
db_path = os.path.join(os.path.dirname(__file__), "../data/databases/mobility.db")
if not os.path.exists(db_path):
    st.warning("⚠️ Base de données non trouvée. Lance `db_initializer.py`.")
else:
    st.success("✅ Base de données chargée.")
