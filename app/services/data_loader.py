# fichier: app/services/data_loader.py

import pandas as pd
import os

# Dossier où sont stockés les fichiers
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")

def load_agency():
    return pd.read_csv(os.path.join(DATA_DIR, "agency.txt"), low_memory=False, encoding='utf-8')

def load_booking_rules():
    return pd.read_csv(os.path.join(DATA_DIR, "booking_rules.txt"), low_memory=False, encoding='utf-8')

def load_calendar():
    return pd.read_csv(os.path.join(DATA_DIR, "calendar.txt"), low_memory=False, encoding='utf-8')

def load_calendar_dates():
    return pd.read_csv(os.path.join(DATA_DIR, "calendar_dates.txt"), low_memory=False, encoding='utf-8')

def load_pathways():
    return pd.read_csv(os.path.join(DATA_DIR, "pathways.txt"), low_memory=False, encoding='utf-8')

def load_routes():
    return pd.read_csv(os.path.join(DATA_DIR, "routes.txt"), low_memory=False, encoding='utf-8')

def load_stop_extensions():
    return pd.read_csv(os.path.join(DATA_DIR, "stop_extensions.txt"), low_memory=False, encoding='utf-8')

def load_stop_times():
    return pd.read_csv(os.path.join(DATA_DIR, "stop_times.txt"), low_memory=False, encoding='utf-8')

def load_stops():
    return pd.read_csv(os.path.join(DATA_DIR, "stops.txt"), low_memory=False, encoding='utf-8')

def load_ticketing_deep_links():
    return pd.read_csv(os.path.join(DATA_DIR, "ticketing_deep_links.txt"), low_memory=False, encoding='utf-8')

def load_transfers():
    return pd.read_csv(os.path.join(DATA_DIR, "transfers.txt"), low_memory=False, encoding='utf-8')

def load_trips():
    return pd.read_csv(os.path.join(DATA_DIR, "trips.txt"), low_memory=False, encoding='utf-8')

def load_arrets_lignes():
    return pd.read_csv(
        os.path.join(DATA_DIR, "arrets_lignes.csv"),
        sep=';',          # Attention ici, séparateur spécial !
        encoding='utf-8'  # Sécurisé
    )

def load_export_trajectoires():
    return pd.read_csv(
        os.path.join(DATA_DIR, "export_trajectoires.csv"),
        sep=',',          # Séparateur classique
        encoding='utf-8'  # Sécurisé
    )

def load_all_data():
    stops = pd.read_csv('data/stops.txt', low_memory=False, encoding='utf-8')
    stop_times = pd.read_csv('data/stop_times.txt', low_memory=False, encoding='utf-8')
    trips = pd.read_csv('data/trips.txt', low_memory=False, encoding='utf-8')
    routes = pd.read_csv('data/routes.txt', low_memory=False, encoding='utf-8')
    transfers = pd.read_csv('data/transfers.txt', low_memory=False, encoding='utf-8')

    return stops, stop_times, trips, routes, transfers


# Exemple d'utilisation:
if __name__ == "__main__":
    agency_df = load_agency()
    print(agency_df.head())
