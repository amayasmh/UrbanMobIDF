import os
import time
import zipfile
import pandas as pd
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

# === Configuration du logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# === Dossiers ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/archives")
FILES_DIR = os.path.join(os.path.dirname(__file__), "../../data/datalake")

def load_file(filename, sep=','):
    try:
        path = os.path.join(DATA_DIR, filename)
        logger.info(f"Chargement du fichier : {path}")
        return pd.read_csv(path, sep=sep, encoding='utf-8', low_memory=False)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {filename} : {e}")
        return pd.DataFrame()

# === Fonctions de chargement ===
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

# === Téléchargement automatisé ===
def load_data_from_web():
    url = "https://new-connect.iledefrance-mobilites.fr/auth/realms/connect-b2b/protocol/openid-connect/auth?client_id=prim&redirect_uri=https://prim.iledefrance-mobilites.fr/fr/&response_type=code&scope=openid%20email"
    download_url = "https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/files/a925e164271e4bca93433756d6a340d1/download/"
    driver = None

    try:
        logger.info("Chargement des variables d'environnement...")
        load_dotenv()
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        edge_driver_path = os.getenv("EDGE_DRIVER_PATH")

        if not email or not password:
            raise ValueError("EMAIL et PASSWORD doivent être définis dans le fichier .env")
        if not edge_driver_path:
            raise ValueError("EDGE_DRIVER_PATH doit être défini dans le fichier .env")

        logger.info("Configuration de Microsoft Edge WebDriver...")
        service = EdgeService(edge_driver_path)
        options = EdgeOptions()
        prefs = {
            "download.default_directory": os.path.abspath(DATA_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Edge(service=service, options=options)
        logger.info("Lancement du navigateur et navigation vers la page de login...")
        driver.get(url)
        time.sleep(2)

        logger.info("Saisie des identifiants...")
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "id-pwd").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(5)

        zip_path = os.path.join(DATA_DIR, "IDFM-gtfs.zip")
        if os.path.exists(zip_path):
            logger.info("Suppression de l'ancien fichier zip...")
            os.remove(zip_path)

        logger.info("Téléchargement du fichier GTFS...")
        driver.get(download_url)
        time.sleep(60)

        if os.path.exists(zip_path):
            logger.info(f"Fichier téléchargé avec succès : {zip_path}")
            logger.info("Décompression du fichier...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(FILES_DIR)
            logger.info("Décompression terminée.")
        else:
            logger.warning("Le fichier n'a pas été téléchargé.")

    except Exception as e:
        logger.exception(f"Une erreur est survenue pendant le chargement des données : {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("Navigateur fermé.")

# === Point d'entrée ===
if __name__ == "__main__":
    load_data_from_web()
