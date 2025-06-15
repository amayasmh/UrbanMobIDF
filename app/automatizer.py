import os
import sys

# Ajouter le chemin racine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services import data_loader, db_initializer

def run():
    try:
        # Chargement des données
        data_loader.load_data_from_web()

        # Initialisation de la base de données
        db_initializer.init_db()

        # Confirmation de l'initialisation
        print("✅ Base de données initialisée et données chargées avec succès.")

    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()