# fichier : app/screens/dashboard.py

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from app.services.db_connector import get_connection


def run():
    st.title("📊 Tableau de bord - Analyse de la mobilité")

    # --- Connexion ---
    conn = get_connection()

    # --- Récupération des lignes disponibles pour filtre ---
    all_routes = pd.read_sql("SELECT DISTINCT route_long_name FROM routes ORDER BY route_long_name", conn)
    route_names = all_routes['route_long_name'].dropna().tolist()
    route_filter = st.selectbox("🧭 Filtrer par ligne :", options=["Toutes"] + route_names)

    # --- Sélection d’une plage horaire ---
    col1, col2 = st.columns(2)
    with col1:
        hour_start = st.selectbox("⏰ Heure de début", list(range(0, 24)), index=6)
    with col2:
        hour_end = st.selectbox("⏰ Heure de fin", list(range(0, 24)), index=20)

    # --- Requête conditionnelle selon filtre ---
    query = f"""
        SELECT 
            s.stop_name,
            st.departure_time,
            r.route_long_name,
            r.route_type
        FROM stop_times st
        JOIN stops s ON st.stop_id = s.stop_id
        JOIN trips t ON t.trip_id = st.trip_id
        JOIN routes r ON r.route_id = t.route_id
        WHERE st.departure_time IS NOT NULL
    """

    params = []
    if route_filter != "Toutes":
        query += " AND r.route_long_name = ?"
        params.append(route_filter)

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # --- Transformation horaire ---
    df['hour'] = df['departure_time'].str[:2].astype(int)
    df = df[(df['hour'] >= hour_start) & (df['hour'] <= hour_end)]

    # --- Statistiques dynamiques ---
    st.subheader("📃 Statistiques filtrées")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre d'arrêts", df['stop_name'].nunique())
    col2.metric("Lignes concernées", df['route_long_name'].nunique())
    col3.metric("Départs comptabilisés", len(df))

    # --- Top stops ---
    st.subheader("📍 Top 10 des arrêts les plus desservis")
    top_stops = df['stop_name'].value_counts().head(10).reset_index()
    top_stops.columns = ["Nom de l'arrêt", "Nombre de passages"]
    st.dataframe(top_stops, use_container_width=True)

    # --- Histogramme ---
    st.subheader("⏱️ Histogramme des départs (heures)")
    hist = df['hour'].value_counts().sort_index()
    fig1, ax1 = plt.subplots()
    ax1.bar(hist.index, hist.values, color="skyblue")
    ax1.set_xlabel("Heure")
    ax1.set_ylabel("Nombre de départs")
    ax1.set_title("Fréquence des départs par heure")
    st.pyplot(fig1)

    # --- Répartition des types de transport ---
    st.subheader("🚇 Répartition des types de transport")
    route_type_map = {
        0: "Tram", 1: "Métro", 2: "Train", 3: "Bus",
        4: "Ferry", 5: "Téléphérique", 6: "Funiculaire", 7: "Trolleybus"
    }
    type_counts = df['route_type'].value_counts().reset_index()
    type_counts.columns = ['route_type', 'nb']
    type_counts['label'] = type_counts['route_type'].map(route_type_map)

    fig2, ax2 = plt.subplots()
    ax2.pie(type_counts['nb'], labels=type_counts['label'], autopct="%1.1f%%", startangle=140)
    ax2.axis("equal")
    ax2.set_title("Répartition des modes")
    st.pyplot(fig2)

    # --- Export CSV ---
    st.subheader("📥 Exporter les données filtrées")
    if st.button("📄 Télécharger en CSV"):
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📎 Télécharger CSV", data=csv, file_name="stats_mobilite_filtrees.csv", mime="text/csv")
