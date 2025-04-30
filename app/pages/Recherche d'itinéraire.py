# fichier : app/pages/Itineraire.py

import streamlit as st
import pandas as pd
from services.db_connector import get_connection
from datetime import datetime
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Recherche d'Itinéraire", page_icon="🚍", layout="wide")
st.title("🔍 Recherche d'Itinéraire")

@st.cache_data
def get_stops():
    conn = get_connection()
    query = "SELECT stop_id, stop_name FROM stops WHERE stop_name IS NOT NULL"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def search_trips(start_stop_id, end_stop_id, selected_time):
    conn = get_connection()
    query = f"""
    WITH destination_stop AS (
        SELECT 
            s.trip_id,
            s.stop_id AS final_stop_id,
            MAX(s.stop_sequence) AS max_sequence
        FROM stop_times s
        GROUP BY s.trip_id
    )
    SELECT DISTINCT 
        t.trip_id,
        r.route_long_name, 
        stops.stop_name AS destination_name,
        s1.departure_time,
        s2.arrival_time
    FROM stop_times s1
    JOIN stop_times s2 ON s1.trip_id = s2.trip_id
    JOIN trips t ON s1.trip_id = t.trip_id
    JOIN routes r ON r.route_id = t.route_id
    JOIN destination_stop ds ON ds.trip_id = t.trip_id
    JOIN stops ON stops.stop_id = ds.final_stop_id
    WHERE s1.stop_id = '{start_stop_id}'
      AND s2.stop_id = '{end_stop_id}'
      AND s1.stop_sequence < s2.stop_sequence
      AND s1.departure_time >= '{selected_time}'
    ORDER BY s1.departure_time ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def get_intermediate_stops(trip_id, start_stop_id, end_stop_id):
    conn = get_connection()
    query = f"""
    SELECT s.stop_id, s.stop_name, st.departure_time, s.stop_lat, s.stop_lon
    FROM stop_times st
    JOIN stops s ON s.stop_id = st.stop_id
    WHERE st.trip_id = '{trip_id}'
      AND (
        (SELECT stop_sequence FROM stop_times WHERE trip_id = '{trip_id}' AND stop_id = '{start_stop_id}') 
          <= st.stop_sequence
        AND
        st.stop_sequence <=
        (SELECT stop_sequence FROM stop_times WHERE trip_id = '{trip_id}' AND stop_id = '{end_stop_id}')
      )
    ORDER BY st.stop_sequence ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Fonction pour récupérer les lignes associées à un arrêt
@st.cache_data
def get_lines_for_stop(stop_id):
    conn = get_connection()
    query = f"""
    SELECT DISTINCT r.route_long_name
    FROM stop_times st
    JOIN trips t ON st.trip_id = t.trip_id
    JOIN routes r ON t.route_id = r.route_id
    WHERE st.stop_id = '{stop_id}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['route_long_name'].dropna().tolist()

# Récupérer les arrêts
stops_df = get_stops()

# Interface utilisateur
col1, col2 = st.columns(2)

with col1:
    start_stop_name = st.selectbox("🛫 Sélectionnez votre point de départ :", stops_df['stop_name'].sort_values())

with col2:
    end_stop_name = st.selectbox("🛬 Sélectionnez votre destination :", stops_df['stop_name'].sort_values())

# Sélection de la date et de l'heure
col3, col4 = st.columns(2)

with col3:
    selected_date = st.date_input("📅 Date de départ", value=datetime.today())

with col4:
    selected_time = st.time_input("🕒 Heure de départ souhaitée", value=datetime.now().time())

# Récupérer les stop_id
start_stop_id = stops_df[stops_df['stop_name'] == start_stop_name]['stop_id'].values[0]
end_stop_id = stops_df[stops_df['stop_name'] == end_stop_name]['stop_id'].values[0]

# Bouton de recherche
if st.button("🔎 Trouver l'itinéraire"):
    if start_stop_id == end_stop_id:
        st.error("🚫 L'arrêt de départ et d'arrivée doivent être différents.")
    else:
        time_filter_str = selected_time.strftime("%H:%M:%S")
        trips_df = search_trips(start_stop_id, end_stop_id, time_filter_str)

        if not trips_df.empty:
            trip = trips_df.iloc[0]

            heure_depart = datetime.strptime(trip['departure_time'], "%H:%M:%S")
            heure_arrivee = datetime.strptime(trip['arrival_time'], "%H:%M:%S")
            duree_trajet = (heure_arrivee - heure_depart).seconds // 60

            st.success(f"✅ Itinéraire trouvé sur **{trip['route_long_name']}** direction **{trip['destination_name']}**")
            st.markdown(f"""
            - 🕒 **Heure de départ** : {trip['departure_time']}
            - 🕒 **Heure d'arrivée** : {trip['arrival_time']}
            - 🕓 **Durée estimée** : {duree_trajet} minutes
            - 📅 **Date** : {selected_date.strftime('%d/%m/%Y')}
            """)

            stops_trajet = get_intermediate_stops(trip['trip_id'], start_stop_id, end_stop_id)
            st.dataframe(stops_trajet[['stop_name', 'departure_time']])

            st.session_state['stops_trajet'] = stops_trajet
            st.session_state['start_stop_name'] = start_stop_name
            st.session_state['end_stop_name'] = end_stop_name
            st.session_state['show_map'] = False
        else:
            st.warning("⚠️ Aucun itinéraire trouvé.")

if st.button("🗺️ Afficher le trajet sur une carte"):
    if 'stops_trajet' in st.session_state:
        st.session_state['show_map'] = True
    else:
        st.warning("❗ Pas de données pour afficher la carte.")

if st.session_state.get('show_map', False):
    if 'stops_trajet' in st.session_state:
        stops_trajet = st.session_state['stops_trajet']
        start_stop_name = st.session_state['start_stop_name']
        end_stop_name = st.session_state['end_stop_name']

        m = folium.Map(location=[stops_trajet['stop_lat'].mean(), stops_trajet['stop_lon'].mean()], zoom_start=13)

        for idx, row in stops_trajet.iterrows():
            lines = get_lines_for_stop(row['stop_id'])
            popup_text = f"🏷️ {row['stop_name']}<br>🚋 Lignes:<br>" + "<br>".join(lines)

            if row['stop_name'] == start_stop_name:
                icon_color = "green"
            elif row['stop_name'] == end_stop_name:
                icon_color = "red"
            else:
                icon_color = "blue"

            folium.Marker(
                location=[row['stop_lat'], row['stop_lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=icon_color, icon="info-sign")
            ).add_to(m)

        points = stops_trajet[['stop_lat', 'stop_lon']].values.tolist()
        folium.PolyLine(points, color="blue", weight=5, opacity=0.8).add_to(m)

        st_folium(m, use_container_width=True)


from services.data_loader import load_all_data
from services.graph_builder import build_graph
from services.route_finder import find_best_route

# Charger les données
stops, stop_times, trips, routes, transfers = load_all_data()

# Construire le graphe
G = build_graph(stops, stop_times, trips, routes, transfers)

# Interface utilisateur
start_stop_name = st.selectbox("Départ", stops['stop_name'])
end_stop_name = st.selectbox("Arrivée", stops['stop_name'])
start_time = st.time_input("Heure de départ", value=None)

if st.button("Trouver un autre itinéraire"):
    start_stop_id = stops[stops['stop_name'] == start_stop_name]['stop_id'].values[0]
    end_stop_id = stops[stops['stop_name'] == end_stop_name]['stop_id'].values[0]

    best_route = find_best_route(G, start_stop_id, start_time.strftime("%H:%M:%S"), end_stop_id)

    if best_route:
        st.success(f"Itinéraire trouvé 🛤️")
        for step in best_route:
            st.write(step)
    else:
        st.error("Aucun itinéraire trouvé 🚫")