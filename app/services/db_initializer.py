import os
import shutil
import sqlite3

import pandas as pd

# === Chemins ===
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "../../data")
DB_PATH = os.path.join(DATA_DIR, "databases/mobility.db")

# === Vérifie si une table existe dans la base ===
def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None

# === Crée des index utiles après chargement ===
def create_indexes(conn):
    cursor = conn.cursor()
    try:
        if table_exists(conn, "stop_times"):
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times (stop_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times (trip_id);")
        if table_exists(conn, "stops"):
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stops_stop_name ON stops (stop_name);")
        conn.commit()
        print("✅ Index créés avec succès.")
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la création des index : {e}")

# === Vérifie l'espace disque disponible ===
def check_disk_space():
    total, used, free = shutil.disk_usage(DATA_DIR)
    free_mb = free // (1024 * 1024)
    print(f"💾 Espace disque libre : {free_mb} Mo")
    if free_mb < 100:
        print("⚠️ Espace disque critique (< 100 Mo) ! Risque d'échec.")
    return free_mb

# === Initialise la base et charge les données ===
def init_db():
    print("🚀 Initialisation de la base de données...")

    free_mb = check_disk_space()
    if free_mb < 50:
        print("🛑 Espace disque insuffisant pour continuer.")
        return

    # Supprimer l'ancienne base si elle est corrompue (optionnel)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("🗑️ Ancienne base supprimée.")
        except Exception as e:
            print(f"❌ Impossible de supprimer l'ancienne base : {e}")
            return

    conn = sqlite3.connect(DB_PATH)

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

        sep = ';' if file_name.endswith('.csv') else ','

        try:
            chunk_size = 100_000
            first_chunk = True
            total_rows = 0

            for chunk in pd.read_csv(file_path, sep=sep, chunksize=chunk_size, encoding='utf-8', low_memory=False):
                chunk.to_sql(table_name, conn, if_exists='replace' if first_chunk else 'append', index=False)
                total_rows += len(chunk)
                first_chunk = False

            print(f"✅ Table `{table_name}` chargée avec succès ({total_rows} lignes).")

        except Exception as e:
            print(f"❌ Erreur lors du chargement de `{file_name}` : {e}")

    create_indexes(conn)
    conn.close()
    print("🎯 Base de données initialisée avec succès !")

# === Lancement direct ===
if __name__ == "__main__":
    init_db()
