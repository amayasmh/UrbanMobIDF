# 🚍 Urban-Mobility-Optimization

---

## 🌐 Introduction

Urban mobility faces persistent challenges such as congestion, accidents, and inefficiencies in public transport. With the rise of open data platforms (Open Data Soft, Data.gov, European Data Portal), it is now possible to harness these data sources to optimize transportation flows and improve commuter experiences.

---

## ❓ Problem Statement

This project aims to provide **real-time traffic predictions** and **intelligent routing recommendations** based on contextual scenarios. Using advanced predictive models like **Random Forests** and **Dijkstra's algorithm**, it empowers:

- Traffic managers to make proactive decisions.
- Citizens to reduce commute times.
- Urban planners to better allocate resources.

Personalized recommendations for both private and public transport users help **reduce traffic jams**, improve **route efficiency**, and **enhance citywide mobility**.

---

## 📦 Key Features

- ✅ Download & process GTFS data from IDFM
- 🧾 Parse and load GTFS data into a **SQLite database**
- 🧠 Build a **weighted directed graph** of the transportation network
- 🔍 Compute **optimal routes** using shortest path algorithms
- ⚡ Streamlit-based user interface (dashboard, alerts, predictions)
- 🔮 Ready for integration with **ML predictions** (RNN, ARIMA)

---

## 📂 Project Structure

```
UrbanMobilDF/
├── app/
│   ├── screens/               # Streamlit screens (Accueil, Alerte, etc.)
│   ├── services/              # Business logic: DB, graph, route finding
│   ├── ui/                    # UI components like sidebar
│   └── assets/                # Logo and static resources
├── data/
│   ├── archives/              # Downloaded ZIP files
│   ├── datalake/              # Extracted & parsed files
│   └── databases/             # mobility.db
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── README.md                  # You’re reading it!
```

---

## 🗃️ Data Sources

- **APIs**
  - [PRIM – Requête globale](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-ivtr-requete_globale)
  - [PRIM – Requête unitaire](https://prim.iledefrance-mobilites.fr/fr/apis/idfm-ivtr-requete_unitaire)
- **Datasets**
  - [Référentiels des arrêts](https://data.iledefrance-mobilites.fr/explore/dataset/arrets/export)
  - [GTFS horaires IDFM](https://prim.iledefrance-mobilites.fr/fr/jeux-de-donnees/offre-horaires-tc-gtfs-idfm)

---

## 🧠 Best Practices

- Use **English** for naming and code.
- Respect naming conventions:
  - `snake_case` for files and variables
  - Verb-based names for functions
- Document your code:
  - Add **docstrings** and inline comments
- Structure execution via `if __name__ == "__main__"`
- Format and lint:
  - `isort`, `black`, `flake8`
- Use `logging` for events, errors, and debug
- Keep code clean using `.gitignore`, `venv`, `requirements.txt`

---

## 🔁 Git Workflow

- Create a branch per feature
- Use **meaningful commit messages**
- Open a **pull request (PR)** to `develop`
- Review and merge only after validation
- Delete branches after merging

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/amayasmh/UrbanMobIDF.git
cd UrbanMobilDF

# Create virtual environment
python -m venv env
source env/bin/activate  # Unix
env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Update EMAIL, PASSWORD, EDGE_DRIVER_PATH in .env
EMAIL="Your Email Here to use IDFM APIs, if you don't have one, create an account on https://prim.iledefrance-mobilites.fr/fr"
PASSWORD="Your Password Here to use IDFM APIs, if you don't have one, create an account on https://prim.iledefrance-mobilites.fr/fr"
EDGE_DRIVER_PATH="/path/to/your/msedgedriver"  # Path to Edge WebDriver

# Install Edge WebDriver
pip install msedge-selenium-tools selenium
# Download and install Microsoft Edge WebDriver
from "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/é"

# Launch data loader to download GTFS data
python app/services/data_loader.py

# Initialize the database
python app/services/db_initializer.py

# Option 1: To automatically run all modules and automatize the process
- Sur windows, use the task scheduler to run the following command 3 times per day (at 8:00, 13:00, and 17:00)
python app/services/automatizer.py or "<path_to_your_python_env> <path_to_your_project>/app/services/automatizer.py"
- On Unix systems, use cron jobs to run the following command 3 times per day (at 8:00, 13:00, and 17:00)
0 8,13,17 * * * /path/to/your/python /path/to/your/project/app/services/automatizer.py

# Option 2: Run modules individually if needed
python app/services/data_loader.py
python app/services/db_initializer.py

# Start the Streamlit app
streamlit run app/Menu.py
```

---

## 🧪 Main Modules

| Module                  | Description                                           |
|-------------------------|-------------------------------------------------------|
| `data_loader.py`        | Download GTFS data and load CSV files                 |
| `db_initializer.py`     | Populate SQLite database from GTFS files              |
| `db_connector.py`       | Manage DB connection and performance indexes          |
| `graph_builder.py`      | Build a NetworkX graph from GTFS trips/stops          |
| `route_finder.py`       | Compute best path between two stop_ids                |
| `automatizer.py.py`     | Launch data_loader and db_initializer automatically   |
| `schedule_estimator.py` | (Planned) ML-based ETA and prediction module          |
| `screens/*.py`          | User-facing UI (Streamlit screens)                    |

---

## 🎯 Objectives Ahead

- Integrate **prediction models** for real-time traffic
- Add **alerts and notification features**
- Support **multi-modal routing** and **priority management**

---

## 👥 Contributors

- [Aghiles SAGHIR](https://www.linkedin.com/in/aghiles-s)
- [Amayas MAHMOUDI](https://www.linkedin.com/in/amayas-mhd)

---

## 📜 License

Project under development for educational and exploratory purposes.
