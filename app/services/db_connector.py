import os
import sqlite3
import logging

# === Configuration du logging ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === Chemin vers la base de données ===
DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/databases/mobility.db")

def get_connection():
    """Retourne une connexion SQLite à la base de données."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        logger.info("Connexion à la base de données établie.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la connexion à la base de données : {e}")
        return None

def initialize_db():
    """Crée les index nécessaires à la performance si non existants."""
    logger.info("Initialisation de la base de données...")
    conn = get_connection()
    if conn is None:
        logger.warning("Annulation : impossible d'établir la connexion à la base.")
        return
    try:
        cursor = conn.cursor()
        logger.info("Création des index si nécessaire...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times (stop_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times (trip_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stops_stop_name ON stops (stop_name);")
        conn.commit()
        logger.info("✅ Index créés avec succès.")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base : {e}")
    finally:
        conn.close()
        logger.info("Connexion à la base de données fermée.")

# === Exemple d’utilisation directe ===
if __name__ == "__main__":
    initialize_db()
