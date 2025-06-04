# fichier : app/screens/admin_congestion_map.py

import pandas as pd
import folium
import streamlit as st
from folium.plugins import HeatMap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from app.services.db_connector import get_connection


def run():
    st.title("📍 Carte des risques de congestion")

    # --- Chargement des données ---
    conn = get_connection()
    stop_times = pd.read_sql("SELECT * FROM stop_times", conn)
    stops = pd.read_sql("SELECT * FROM stops", conn)
    trips = pd.read_sql("SELECT * FROM trips", conn)
    conn.close()

    # Préparation des données
    stop_times = stop_times.dropna(subset=["departure_time"])
    stop_times = stop_times.merge(trips[["trip_id", "route_id"]], on="trip_id", how="left")

    # Extraction heure
    stop_times["hour"] = stop_times["departure_time"].str[:2].astype(int)

    # Comptage du trafic
    traffic_df = stop_times.groupby(["stop_id", "hour"]).size().reset_index(name="traffic")
    data = traffic_df.merge(stops[["stop_id", "stop_lat", "stop_lon"]], on="stop_id", how="left")
    data = data.dropna()

    # Modèle IA (Random Forest)
    features = data[["hour"]]
    target = data["traffic"]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(features, target)

    # Prédiction du trafic futur (exemple 8h à 10h)
    future_hours = pd.DataFrame({"hour": list(range(8, 11))})
    predicted_data = pd.DataFrame()
    for hour in future_hours["hour"]:
        subset = data[data["hour"] == hour].copy()
        subset["predicted_traffic"] = model.predict(subset[["hour"]])
        predicted_data = pd.concat([predicted_data, subset])

    st.subheader("🗺️ Carte prédictive des congestions")

    m = folium.Map(location=[48.85, 2.35], zoom_start=11)

    heat_data = [
        [row["stop_lat"], row["stop_lon"], row["predicted_traffic"]]
        for _, row in predicted_data.iterrows()
    ]
    HeatMap(heat_data, radius=12, blur=15, min_opacity=0.3, max_val=predicted_data["predicted_traffic"].max()).add_to(m)

    st.markdown("Zones en rouge = fort trafic prévu")
    st.components.v1.html(m.get_root().render(), height=600, scrolling=False)

    # Option d’export CSV
    st.subheader("📤 Exporter les prédictions")
    if st.button("💾 Télécharger en CSV"):
        csv = predicted_data.to_csv(index=False).encode("utf-8")
        st.download_button("📎 Export CSV", data=csv, file_name="previsions_congestion.csv", mime="text/csv")
