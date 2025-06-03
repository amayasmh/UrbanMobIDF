# fichier : app/utils.py

import streamlit as st
import requests

# Clé pour stocker la page active dans la session
SESSION_PAGE_KEY = "current_page"

def get_current_page():
    """
    Récupère la page active depuis la session utilisateur.
    Si aucune page n'est définie, retourne 'home' par défaut.
    """
    return st.session_state.get(SESSION_PAGE_KEY, "home")

def set_current_page(page_name):
    """
    Définit la page active dans la session utilisateur.
    """
    st.session_state[SESSION_PAGE_KEY] = page_name

def calculate_co2(schedule):
    co2_by_mode = {
        "Train": 14, "Métro": 3, "Tram": 4,
        "Bus": 89, "Trolleybus": 65, "Navette": 110,
        "Correspondance": 0
    }
    total = 0
    for step in schedule:
        g_per_min = co2_by_mode.get(step['mode'], 50)
        total += g_per_min * step['duration_min']
    return total

def get_weather(lat, lon, arrival_dt):
    if not lat or not lon:
        return "Météo non disponible", None
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,weathercode&timezone=auto"
            f"&start_date={arrival_dt.date()}&end_date={arrival_dt.date()}"
        )
        res = requests.get(url)
        data = res.json()

        target_hour = arrival_dt.replace(minute=0, second=0, microsecond=0).isoformat()
        times = data["hourly"]["time"]
        temps = data["hourly"]["temperature_2m"]
        codes = data["hourly"]["weathercode"]

        if target_hour in times:
            idx = times.index(target_hour)
            temp = temps[idx]
            code = codes[idx]
        else:
            temp = temps[0]
            code = codes[0]

        desc = weather_description(code)
        return f"{desc}, {temp}°C", code
    except Exception:
        return "Météo non disponible", None

def weather_description(code):
    mapping = {
        0: "☀️ Ensoleillé", 1: "🌤️ Partiellement nuageux", 2: "⛅ Nuageux",
        3: "☁️ Très nuageux", 45: "🌫️ Brouillard", 48: "🌫️ Brouillard givrant",
        51: "🌦️ Bruine légère", 61: "🌧️ Pluie légère", 63: "🌧️ Pluie modérée",
        65: "🌧️ Pluie forte", 71: "❄️ Neige légère", 73: "❄️ Neige modérée",
        75: "❄️ Neige forte", 95: "🌩️ Orages"
    }
    return mapping.get(code, "Conditions météo inconnues")
