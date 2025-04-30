import pandas as pd
import sqlite3
import os

# Chemin vers dossier data
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")

# Connexion à la base SQLite
DB_PATH = os.path.join(DATA_DIR, "mobility.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)

    # Fichiers à charger
    files = {
        "agency": "agency.txt",
        "booking_rules": "booking_rules.txt",
        "calendar": "calendar.txt",
        "calendar_dates": "calendar_dates.txt",
        "pathways": "pathways.txt",
        "routes": "routes.txt",
        "stop_extensions": "stop_extensions.txt",
        "stop_times": "stop_times.txt",
        "stops": "stops.txt",
        "ticketing_deep_links": "ticketing_deep_links.txt",
        "transfers": "transfers.txt",
        "trips": "trips.txt",
        "arrets_lignes": "arrets_lignes.csv"
    }

    for table_name, file_name in files.items():
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            print(f"⚠️  Fichier manquant : {file_name}")
            continue

        sep = ';' if file_name.endswith('.csv') and "arrets_lignes" in file_name else ','

        try:
            chunk_size = 100_000
            first_chunk = True
            total_rows = 0

            for chunk in pd.read_csv(file_path, sep=sep, chunksize=chunk_size, low_memory=False, encoding='utf-8'):
                chunk.to_sql(table_name, conn, if_exists='replace' if first_chunk else 'append', index=False)
                total_rows += len(chunk)
                first_chunk = False

            print(f"✅ Table {table_name} créée avec {total_rows} lignes.")

        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_name} : {e}")

    conn.close()
    print("🎯 Base de données initialisée !")

# Exécution directe
if __name__ == "__main__":
    init_db()
