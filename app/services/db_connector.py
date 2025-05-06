import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/databases/mobility.db")

def get_connection():
    """Retourne une connexion SQLite à la base de données."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        return None

def initialize_db():
    """Crée les index nécessaires à la performance si non existants."""
    conn = get_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        # Création d'index utiles
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times (stop_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times (trip_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stops_stop_name ON stops (stop_name);")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation de la base : {e}")
    finally:
        conn.close()

# Exemple d’utilisation directe
if __name__ == "__main__":
    initialize_db()
