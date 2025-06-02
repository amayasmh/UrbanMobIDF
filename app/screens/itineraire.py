import logging
import os
import pickle
from datetime import datetime, timedelta

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from app.services.db_connector import get_connection
from app.services.graph_builder import build_graph
from app.services.route_finder import find_best_path
from app.services.schedule_estimator import estimate_schedule

# === Logging config ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === Paths ===
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "../../data")
DB_PATH = os.path.join(DATA_DIR, "databases/mobility.db")
GRAPH_PATH = os.path.join(DATA_DIR, "graphe_transport.pkl")

def run():
    st.title("🗺️ Recherche d'Itinéraire")

    @st.cache_data
    def load_data_from_db():
        conn = get_connection()
        stops = pd.read_sql("SELECT * FROM stops", conn)
        stop_times = pd.read_sql("SELECT * FROM stop_times", conn)
        trips = pd.read_sql("SELECT * FROM trips", conn)
        routes = pd.read_sql("SELECT * FROM routes", conn)
        transfers = pd.read_sql("SELECT * FROM transfers", conn)
        conn.close()
        return stops, stop_times, trips, routes, transfers

    @st.cache_data
    def get_stops():
        conn = get_connection()
        df = pd.read_sql("SELECT DISTINCT stop_id, stop_name FROM stops WHERE stop_name IS NOT NULL", conn)
        conn.close()
        return df

    stops_df = get_stops()
    stop_names = stops_df['stop_name'].sort_values().unique()

    col1, col2 = st.columns(2)
    with col1:
        start_name = st.selectbox("🛫 Point de départ", stop_names)
    with col2:
        end_name = st.selectbox("🛬 Destination", stop_names)

    col3, col4 = st.columns(2)
    with col3:
        selected_date = st.date_input("📅 Date", value=datetime.today())
    with col4:
        selected_time = st.time_input("🕒 Heure", value=datetime.now().time())

    start_id = stops_df[stops_df['stop_name'] == start_name]['stop_id'].values[0]
    end_id = stops_df[stops_df['stop_name'] == end_name]['stop_id'].values[0]

    logger.info(f"Itinéraire demandé : {start_name} ({start_id}) → {end_name} ({end_id}) à {selected_time}")

    if st.button("🔀 Itinéraire optimisé (avec correspondances)"):
        stops, stop_times, trips, routes, transfers = load_data_from_db()
        if os.path.exists(GRAPH_PATH):
            with open(GRAPH_PATH, "rb") as f:
                G, name_to_id, id_to_name = pickle.load(f)
        else:
            G, name_to_id, id_to_name = build_graph(stops, stop_times, trips, routes, transfers)

        if start_id not in G.nodes or end_id not in G.nodes:
            st.warning("🚫 Départ ou arrivée non trouvés dans le graphe.")
            return

        path = find_best_path(G, start_id, end_id)
        if not path:
            st.error("❌ Aucun chemin trouvé dans le graphe.")
            return

        departure_dt = datetime.combine(selected_date, selected_time)
        schedule = estimate_schedule(path, departure_dt, stop_times, trips, routes, G)
        total_duration_min = (schedule[-1]['arrival_dt'] - schedule[0]['departure_dt']).seconds // 60

        st.session_state['itineraire_result'] = {
            "schedule": schedule,
            "start_name": start_name,
            "end_name": end_name,
            "departure_time": selected_time,
            "arrival_time": schedule[-1]['arrival_dt'].strftime('%H:%M'),
            "duration": total_duration_min
        }

    if "itineraire_result" in st.session_state:
        result = st.session_state["itineraire_result"]
        schedule = result["schedule"]

        st.success(f"🧭 Trajet trouvé en {result['duration']} minutes avec correspondances")
        st.markdown(f"""
        - 🟢 **Départ** : {result['start_name']} à {schedule[0]['departure_dt'].strftime('%H:%M')}
        - 🔴 **Arrivée** : {result['end_name']} à {result['arrival_time']}
        - ⌛ **Durée estimée** : {result['duration']} minutes
        - 🧩 **Nombre d'étapes** : {len(schedule)}
        """)

        df = pd.DataFrame([{
            "Arrêt": s['stop_name'],
            "Mode": s['mode'],
            "Ligne": s['route_name'],
            "Départ": s['departure_dt'].strftime("%H:%M"),
            "Arrivée": s['arrival_dt'].strftime("%H:%M"),
            "Durée (min)": s['duration_min']
        } for s in schedule])
        st.dataframe(df)

        st.markdown("### 🗺️ Trajet sur la carte")
        coords = [(s['lat'], s['lon']) for s in schedule if s['lat'] and s['lon']]
        if not coords:
            st.warning("❗ Aucune position géographique trouvée pour le trajet.")
        else:
            m = folium.Map(location=coords[0], zoom_start=13)
            for idx, step in enumerate(schedule):
                if not step['lat'] or not step['lon']:
                    continue
                color = "green" if idx == 0 else "red" if idx == len(schedule) - 1 else "blue"
                folium.Marker(
                    location=[step['lat'], step['lon']],
                    popup=f"{step['stop_name']} ({step['departure_dt'].strftime('%H:%M')} → {step['arrival_dt'].strftime('%H:%M')})\nLigne: {step['route_name']}",
                    icon=folium.Icon(color=color)
                ).add_to(m)
            folium.PolyLine(coords, color="blue", weight=4).add_to(m)
            st_folium(m, use_container_width=True)
