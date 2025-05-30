# fichier: app/services/data_loader.py

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
from dotenv import load_dotenv


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

def load_data_from_web():
    """
    Fonction pour charger les données depuis le web.
    """
    url = "https://new-connect.iledefrance-mobilites.fr/auth/realms/connect-b2b/protocol/openid-connect/auth?client_id=prim&redirect_uri=https://prim.iledefrance-mobilites.fr/fr/&response_type=code&scope=openid%20email"

    # Déclare driver en dehors du try
    driver = None

    try:

        # Charger les variables d'environnement depuis le fichier .env
        load_dotenv()

        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        url_chrome_driver = os.getenv("CHROME_DRIVER_URL")
        if not email or not password:
            raise ValueError(
                "Les variables d'environnement EMAIL et PASSWORD doivent être définies dans le fichier .env")

        # Spécifie le chemin du ChromeDriver via Service
        service = Service(url_chrome_driver)
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        time.sleep(2)  # Attente plus fiable que implicitly_wait ici

        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "id-pwd").send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        time.sleep(5)  # Temps d'attente après login

        # Télécharger le fichier depuis ce lien en le tapant dans la barre d'adresse après le login
        download_url = "https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/files/a925e164271e4bca93433756d6a340d1/download/"
        driver.get(download_url)
        time.sleep(60)  # Attendre le téléchargement
        # Vérifier si le fichier a été téléchargé
        download_path = os.path.join(DATA_DIR, "IDFM-gtfs.zip")
        if os.path.exists(download_path):
            print(f"Fichier téléchargé avec succès : {download_path}")
        else:
            print("Le fichier n'a pas été téléchargé.")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

    finally:
        if driver is not None:
            driver.quit()

# Exemple d'utilisation
if __name__ == "__main__":
    load_data_from_web()
