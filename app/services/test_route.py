import logging
import os
import pickle
import sqlite3

import networkx as nx
import pandas as pd

# === Logging ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def time_to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s


# === Chemins ===
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "../../data")
DB_PATH = os.path.join(DATA_DIR, "databases/mobility.db")
GRAPH_PATH = os.path.join(DATA_DIR, "graphe_transport.pkl")

# === Dictionnaire des types GTFS vers noms lisibles ===
GTFS_ROUTE_TYPES = {
    0: "Tram", 1: "Métro", 2: "Train", 3: "Bus", 4: "Ferry",
    5: "Téléphérique", 6: "Funiculaire", 7: "Trolleybus", 11: "Navette"
}

# === Initialisation ===
G = None
name_to_id = {}
id_to_name = {}

# === Chargement ou construction du graphe ===
if os.path.exists(GRAPH_PATH):
    logging.info("Chargement du graphe depuis graphe_transport.pkl...")
    with open(GRAPH_PATH, "rb") as f:
        G, name_to_id, id_to_name = pickle.load(f)
else:
    logging.info("Construction du graphe (fichier non trouvé)...")

    conn = sqlite3.connect(DB_PATH)
    stops = pd.read_sql_query("SELECT * FROM stops", conn)
    stop_times = pd.read_sql_query("SELECT * FROM stop_times", conn)
    transfers = pd.read_sql_query("SELECT * FROM transfers", conn)
    trips = pd.read_sql_query("SELECT * FROM trips", conn)
    routes = pd.read_sql_query("SELECT * FROM routes", conn)

    stop_times['arrival_time'] = stop_times['arrival_time'].fillna("00:00:00").apply(time_to_seconds)
    stop_times['departure_time'] = stop_times['departure_time'].fillna("00:00:00").apply(time_to_seconds)
    stop_times = stop_times.sort_values(by=['trip_id', 'stop_sequence'])
    stop_times['next_stop_id'] = stop_times.groupby('trip_id')['stop_id'].shift(-1)
    stop_times['next_arrival_time'] = stop_times.groupby('trip_id')['arrival_time'].shift(-1)
    stop_times['next_departure_time'] = stop_times.groupby('trip_id')['departure_time'].shift(-1)
    stop_times['travel_time'] = stop_times['next_arrival_time'] - stop_times['departure_time']

    name_to_id = stops.dropna(subset=['stop_name']).drop_duplicates('stop_name').set_index('stop_name')[
        'stop_id'].to_dict()
    id_to_name = stops.set_index('stop_id')['stop_name'].to_dict()
    trip_to_route = trips.set_index('trip_id')['route_id'].to_dict()
    route_info = routes.set_index('route_id')[['route_short_name', 'route_type']].to_dict(orient='index')

    G = nx.DiGraph()
    for _, row in stop_times.dropna(subset=['next_stop_id']).iterrows():
        from_stop = row['stop_id']
        to_stop = row['next_stop_id']
        travel_time = row['travel_time']
        trip_id = row['trip_id']
        route_id = trip_to_route.get(trip_id)
        route = route_info.get(route_id, {})
        line_name = route.get('route_short_name', '??')
        mode = GTFS_ROUTE_TYPES.get(route.get('route_type'), '??')

        if travel_time >= 0:
            G.add_edge(from_stop, to_stop, weight=travel_time, line=line_name, mode=mode)

    for _, row in transfers.iterrows():
        G.add_edge(row['from_stop_id'], row['to_stop_id'], weight=row.get('min_transfer_time', 60), line='TRANSFERT',
                   mode='Correspondance')

    with open(GRAPH_PATH, "wb") as f:
        pickle.dump((G, name_to_id, id_to_name), f)
    logging.info("Graphe sauvegardé dans graphe_transport.pkl")
    conn.close()

# === Boucle interactive ===
while True:
    print("\n============== NOUVEL ITINÉRAIRE ==============")
    start_name = input("Nom de la station de départ (ou 'exit' pour quitter) : ").strip()
    if start_name.lower() == "exit":
        break

    end_name = input("Nom de la station d’arrivée : ").strip()

    if start_name not in name_to_id or end_name not in name_to_id:
        logging.warning("Station non trouvée.")
        print("❌ Erreur : une des stations est inconnue.")
        continue

    start_stop = name_to_id[start_name]
    end_stop = name_to_id[end_name]

    try:
        path = nx.dijkstra_path(G, start_stop, end_stop, weight='weight')
        total_time = nx.dijkstra_path_length(G, start_stop, end_stop, weight='weight')

        print("\n🗺️  Itinéraire (le plus rapide) :")

        previous_line = None
        previous_mode = None
        adjusted_time = total_time
        correspondance_count = 0

        for i in range(len(path) - 1):
            from_id = path[i]
            to_id = path[i + 1]
            edge_data = G.edges[from_id, to_id]
            line = edge_data.get('line', '?')
            mode = edge_data.get('mode', '?')
            from_name = id_to_name.get(from_id, from_id)

            if previous_line is not None and (line != previous_line or mode != previous_mode):
                print(f" ↪️  Correspondance : changer de {previous_mode} {previous_line} → {mode} {line} (ajout 5 min)")
                adjusted_time += 300
                correspondance_count += 1

            print(f" → {from_name} (via {mode} {line})")
            previous_line = line
            previous_mode = mode

        # Dernier arrêt
        print(f" → {id_to_name.get(path[-1])}")

        minutes = int(adjusted_time // 60)
        seconds = int(adjusted_time % 60)
        print(
            f"\n⏱️  Durée estimée du trajet (avec {correspondance_count} correspondance(s)) : {minutes} minutes {seconds} secondes")

    except nx.NetworkXNoPath:
        print("❌ Aucun chemin trouvé entre ces deux stations.")
    except nx.NodeNotFound as e:
        print(f"❌ Erreur de nœud : {e}")

