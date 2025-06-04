# fichier : app/services/congestion_handler.py

import pandas as pd
import os
import pickle

from collections import Counter
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from app.services.db_connector import get_connection

CONGESTION_ANALYSIS_PATH = os.path.join(os.path.dirname(__file__), "../../data/congestion_model.pkl")
CONGESTION_LOG_PATH = os.path.join(os.path.dirname(__file__), "../../data/congestion_suggestions.csv")


def train_congestion_model():
    conn = get_connection()
    stop_times = pd.read_sql("SELECT stop_id, departure_time FROM stop_times", conn)
    stops = pd.read_sql("SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops", conn)
    conn.close()

    stop_times = stop_times.dropna(subset=['departure_time'])
    stop_times['hour'] = stop_times['departure_time'].str.slice(0, 2).astype(int)
    traffic = stop_times.groupby(['stop_id', 'hour']).size().reset_index(name="traffic")

    traffic = traffic.merge(stops, on="stop_id", how="left")

    le = LabelEncoder()
    traffic['stop_id_enc'] = le.fit_transform(traffic['stop_id'])

    model = RandomForestRegressor()
    model.fit(traffic[['stop_id_enc', 'hour']], traffic['traffic'])

    with open(CONGESTION_ANALYSIS_PATH, "wb") as f:
        pickle.dump((model, le), f)

    return model, le


def predict_congestion(stop_id, hour):
    if not os.path.exists(CONGESTION_ANALYSIS_PATH):
        return None

    with open(CONGESTION_ANALYSIS_PATH, "rb") as f:
        model, le = pickle.load(f)

    if stop_id not in le.classes_:
        return 0
    stop_encoded = le.transform([stop_id])[0]
    return model.predict([[stop_encoded, hour]])[0]


def should_avoid_congestion(path, dt):
    """
    Analyse un chemin et détecte s’il traverse des zones à risque à l’heure prévue.
    Retourne une liste des arrêts à éviter.
    """
    hour = dt.hour
    problematic_stops = []

    for stop_id in path:
        congestion_score = predict_congestion(stop_id, hour)
        if congestion_score and congestion_score > 150:  # seuil à ajuster
            problematic_stops.append(stop_id)

    return problematic_stops


def log_admin_suggestion(schedule, congested_stops):
    data = []
    for step in schedule:
        if step['from_stop'] in congested_stops:
            data.append({
                "datetime": datetime.now().isoformat(),
                "stop_id": step['from_stop'],
                "stop_name": step['stop_name'],
                "lat": step['lat'],
                "lon": step['lon'],
                "mode": step['mode'],
                "route_name": step['route_name'],
                "congestion_risk": True
            })

    if not data:
        return

    df = pd.DataFrame(data)
    if os.path.exists(CONGESTION_LOG_PATH):
        df.to_csv(CONGESTION_LOG_PATH, mode='a', header=False, index=False)
    else:
        df.to_csv(CONGESTION_LOG_PATH, index=False)

def predict_congested_stops(threshold=200):
    """
    Prédit les arrêts congestionnés à partir du volume de passages enregistrés.
    Retourne une liste des stop_id à éviter si > seuil (par défaut : 100 passages).
    """
    conn = get_connection()
    query = """
        SELECT stop_id
        FROM stop_times
        WHERE departure_time IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()

    stop_counts = df['stop_id'].value_counts()
    congested_stops = stop_counts[stop_counts > threshold].index.tolist()

    # Optionnel : sauvegarde pour suivi
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = os.path.join("data", f"congested_stops_{timestamp}.csv")
    pd.DataFrame({'stop_id': congested_stops}).to_csv(save_path, index=False)

    return congested_stops

def should_avoid_congestion():
    """
    Décide si l'utilisateur/admin souhaite éviter les zones congestionnées.
    Peut être piloté depuis l'interface Streamlit.
    """
    import streamlit as st
    return st.checkbox("🚧 Éviter les zones à forte congestion", value=True)
