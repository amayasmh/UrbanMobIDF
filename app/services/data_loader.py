# fichier: app/services/data_loader.py

import pandas as pd
import os

# Dossier où sont stockés les fichiers
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/datalake")

def load_file(filename, sep=','):
    try:
        return pd.read_csv(os.path.join(DATA_DIR, filename), sep=sep, encoding='utf-8', low_memory=False)
    except Exception as e:
        print(f"Erreur lors du chargement de {filename} : {e}")
        return pd.DataFrame()

# Fonctions spécifiques
def load_agency(): return load_file("agency.txt")
def load_booking_rules(): return load_file("booking_rules.txt")
def load_calendar(): return load_file("calendar.txt")
def load_calendar_dates(): return load_file("calendar_dates.txt")
def load_pathways(): return load_file("pathways.txt")
def load_routes(): return load_file("routes.txt")
def load_stop_extensions(): return load_file("stop_extensions.txt")
def load_stop_times(): return load_file("stop_times.txt")
def load_stops(): return load_file("stops.txt")
def load_ticketing_deep_links(): return load_file("ticketing_deep_links.txt")
def load_transfers(): return load_file("transfers.txt")
def load_trips(): return load_file("trips.txt")
def load_arrets_lignes(): return load_file("arrets_lignes.csv", sep=';')
def load_export_trajectoires(): return load_file("export_trajectoires.csv")

# Exemple d'utilisation
if __name__ == "__main__":
    df = load_agency()
    print(df.head())
