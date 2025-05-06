# fichier : app/screens/itineraire.py

import streamlit as st
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium

from app.services.db_connector import get_connection
from app.services.graph_builder import build_graph
from app.services.route_finder import find_best_route

def run():
    st.title("🗺️ Recherche d'Itinéraire")

    # ---------- Chargement des données ----------
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

    @st.cache_data
    def search_trips_direct(start_id, end_id, time_str):
        conn = get_connection()
        query = """
            SELECT DISTINCT
                t.trip_id,
                r.route_long_name,
                s_end.stop_name AS destination_name,
                s1.departure_time,
                s2.arrival_time
            FROM stop_times s1
            JOIN stop_times s2 ON s1.trip_id = s2.trip_id
            JOIN trips t ON t.trip_id = s1.trip_id
            JOIN routes r ON r.route_id = t.route_id
            JOIN stops s_end ON s_end.stop_id = s2.stop_id
            WHERE s1.stop_id = ? AND s2.stop_id = ?
              AND s1.stop_sequence < s2.stop_sequence
              AND s1.departure_time >= ?
            ORDER BY s1.departure_time ASC
        """
        df = pd.read_sql_query(query, conn, params=(start_id, end_id, time_str))
        conn.close()
        return df

    @st.cache_data
    def get_intermediate_stops(trip_id, start_id, end_id):
        conn = get_connection()
        query = """
            SELECT s.stop_name, s.stop_lat, s.stop_lon, st.departure_time
            FROM stop_times st
            JOIN stops s ON s.stop_id = st.stop_id
            WHERE st.trip_id = ?
              AND st.stop_sequence BETWEEN
                  (SELECT stop_sequence FROM stop_times WHERE trip_id = ? AND stop_id = ?)
                  AND
                  (SELECT stop_sequence FROM stop_times WHERE trip_id = ? AND stop_id = ?)
            ORDER BY st.stop_sequence
        """
        df = pd.read_sql_query(query, conn, params=(trip_id, trip_id, start_id, trip_id, end_id))
        conn.close()
        return df

    # ---------- Interface utilisateur ----------
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

    # ---------- Itinéraire direct ----------
    if st.button("🔍 Itinéraire direct"):
        if start_id == end_id:
            st.error("❗ L'arrêt de départ et d'arrivée doivent être différents.")
        else:
            trips = search_trips_direct(start_id, end_id, selected_time.strftime("%H:%M:%S"))
            if trips.empty:
                st.warning("⚠️ Aucun itinéraire direct trouvé.")
            else:
                trip = trips.iloc[0]
                steps = get_intermediate_stops(trip['trip_id'], start_id, end_id)

                st.session_state['trip_result'] = {
                    'mode': 'direct',
                    'trip': trip.to_dict(),
                    'steps': steps.to_dict(orient='records'),
                    'start_name': start_name,
                    'end_name': end_name
                }

    # ---------- Itinéraire optimisé ----------
    if st.button("🔀 Itinéraire optimisé (avec correspondances)"):
        st.info("📦 Chargement des données...")
        stops, stop_times, trips, routes, transfers = load_data_from_db()

        st.info("🧱 Construction du graphe...")
        G = build_graph(stops, stop_times, trips, routes, transfers)

        st.info("🧭 Recherche du chemin optimal avec correspondances...")
        result = find_best_route(G, start_id, selected_time.strftime("%H:%M:%S"), end_id)

        if result:
            st.success(f"✅ Trajet trouvé en {result['total_duration_min']} minutes avec correspondances")
            st.session_state['trip_result'] = {
                'mode': 'optimal',
                'path': result['path'],
                'steps': result['steps'],
                'total_duration': result['total_duration_min'],
                'start_name': start_name,
                'end_name': end_name
            }
        else:
            st.warning("❌ Aucun itinéraire trouvé avec correspondances.")

    # ---------- Résultats ----------
    if 'trip_result' in st.session_state:
        result = st.session_state['trip_result']
        st.divider()

        if result['mode'] == 'direct':
            trip = result['trip']
            steps = pd.DataFrame(result['steps'])
            st.success(f"🚍 Itinéraire direct : {trip['route_long_name']} → {trip['destination_name']}")
            st.markdown(f"""
            - 🕒 **Départ** : {trip['departure_time']}
            - 🕒 **Arrivée** : {trip['arrival_time']}
            - ⏱️ **Durée estimée** : {int((pd.to_datetime(trip['arrival_time']) - pd.to_datetime(trip['departure_time'])).total_seconds() // 60)} min
            - 🚏 **Nombre d’arrêts** : {len(steps)}
            """)
            st.dataframe(steps[['stop_name', 'departure_time']])

            m = folium.Map(location=[steps['stop_lat'].mean(), steps['stop_lon'].mean()], zoom_start=13)
            for idx, row in steps.iterrows():
                color = "blue"
                if row['stop_name'] == result['start_name']:
                    color = "green"
                elif row['stop_name'] == result['end_name']:
                    color = "red"
                folium.Marker(
                    location=[row['stop_lat'], row['stop_lon']],
                    popup=row['stop_name'],
                    icon=folium.Icon(color=color)
                ).add_to(m)
            folium.PolyLine(steps[['stop_lat', 'stop_lon']].values.tolist(), color="blue").add_to(m)
            st_folium(m, use_container_width=True)

        elif result['mode'] == 'optimal':
            steps = result['steps']
            st.success(f"🧭 Itinéraire optimal trouvé en {result['total_duration']} minutes avec correspondances")
            for i, step in enumerate(steps):
                emoji = "🚶" if step['type'] == 'transfer' else "🚌"
                st.markdown(
                    f"**Étape {i+1}** : {emoji} `{step['route_name']}` "
                    f"→ {step['from_stop']} → {step['to_stop']} "
                    f"({step['duration_min']} min, {step['departure_time']} → {step['arrival_time']})"
                )
