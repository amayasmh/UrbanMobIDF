# fichier : app/screens/accueil.py

import streamlit as st
import os
import pandas as pd
from app.services.db_connector import get_connection

def run():
    st.title("🏙️ Accueil - Optimisation de la Mobilité Urbaine")

    st.markdown("""
    Bienvenue dans l'application d'optimisation de la mobilité urbaine. 
    Naviguez à travers les différents onglets pour explorer les fonctionnalités disponibles.
    """)

    st.markdown("## 📊 Statistiques en temps réel")

    # Chargement rapide des stats clés depuis la base
    conn = get_connection()
    stops = pd.read_sql("SELECT COUNT(*) AS n FROM stops", conn).iloc[0]["n"]
    trips = pd.read_sql("SELECT COUNT(*) AS n FROM trips", conn).iloc[0]["n"]
    routes = pd.read_sql("SELECT COUNT(*) AS n FROM routes", conn).iloc[0]["n"]
    transfers = pd.read_sql("SELECT COUNT(*) AS n FROM transfers", conn).iloc[0]["n"]
    conn.close()

    animation_css = """
        <style>
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.4); }
            70% { box-shadow: 0 0 10px 10px rgba(0, 0, 0, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
        }
        .stat-card {
            animation: pulse 2s infinite;
            transition: transform 0.2s ease-in-out;
        }
        .stat-card:hover {
            transform: scale(1.05);
        }
        </style>
    """
    st.markdown(animation_css, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="stat-card" style="background-color:#4CAF50;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:white;margin:0">🚌 Lignes</h3>
                <p style="color:white;font-size:24px;margin:0">{routes}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="stat-card" style="background-color:#2196F3;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:white;margin:0">📍 Arrêts</h3>
                <p style="color:white;font-size:24px;margin:0">{stops}</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="stat-card" style="background-color:#FF9800;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:white;margin:0">🛣️ Trajets</h3>
                <p style="color:white;font-size:24px;margin:0">{trips}</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="stat-card" style="background-color:#9C27B0;padding:20px;border-radius:10px;text-align:center">
                <h3 style="color:white;margin:0">🔁 Correspondances</h3>
                <p style="color:white;font-size:24px;margin:0">{transfers}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    # Total des commissions CO2 générées dans l'application
    st.markdown("## 🌱 Impact Environnemental")
    col = st.columns(1)[0]
    # Récupérer les données de CO2 économisé depuis le fichier data/commissions_log.csv
    if not os.path.exists("data/emission_log.csv"):
        total_co2 = 0
    else:
        emissions_df = pd.read_csv("data/emission_log.csv", header=0)
        total_co2 = emissions_df['co2_total'].sum() / 2 if 'co2_total' in emissions_df.columns else 0

        with col:
            st.markdown(f"""
                <div class="stat-card" style="background-color:#4CAF50;padding:20px;border-radius:10px;text-align:center">
                    <h3 style="color:white;margin:0">🌍 Empreinte carbone calculée</h3>
                    <p style="color:white;font-size:24px;margin:0">{total_co2/1000:.2f} kg</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col = st.columns(2)[0]
    # Récupérer les données de CO2 économisé depuis le fichier data/commissions_log.csv
    if not os.path.exists("data/emission_log.csv"):
        total_co2 = 0
    else:
        emissions_df = pd.read_csv("data/emission_log.csv", header=0)
        total_co2 = emissions_df['co2_total'].sum() / 2 if 'co2_total' in emissions_df.columns else 0

        with col:
            st.markdown(f"""
                <div class="stat-card" style="background-color:#4CAF50;padding:20px;border-radius:10px;text-align:center">
                    <h3 style="color:white;margin:0">🌍 Empreinte carbone calculée</h3>
                    <p style="color:white;font-size:24px;margin:0">{total_co2/1000:.2f} kg</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("## 🌦️ Prévisions Météo Paris")
    st.components.v1.html(
        '<iframe src="https://www.meteo-villes.com/widget/prevision-meteo?type=expertized&amp;city=2&amp;wgt=full&amp;days=5&amp;bg-clr=ffffff&amp;ft-clr=475dff" frameborder="0" style="width: 340px; height: 375px;"></iframe>',
        height=400,
        scrolling=False
    )
