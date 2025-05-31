import os
import logging
import pickle
import pandas as pd
import networkx as nx

GRAPH_PATH = os.path.join(os.path.dirname(__file__), "../../data/graphe_transport.pkl")
GTFS_ROUTE_TYPES = {
    0: "Tram", 1: "Métro", 2: "Train", 3: "Bus", 4: "Ferry",
    5: "Téléphérique", 6: "Funiculaire", 7: "Trolleybus", 11: "Navette"
}

logger = logging.getLogger(__name__)

def time_to_seconds(t):
    try:
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0

def build_graph(stops, stop_times, trips, routes):
    if os.path.exists(GRAPH_PATH):
        logger.info("📦 Chargement du graphe depuis graphe_transport.pkl...")
        with open(GRAPH_PATH, "rb") as f:
            G, name_to_id, id_to_name = pickle.load(f)
        return G, name_to_id, id_to_name

    logger.info("🚧 Construction du graphe depuis les données brutes...")
    G = nx.DiGraph()

    stop_times['arrival_time'] = stop_times['arrival_time'].fillna("00:00:00").apply(time_to_seconds)
    stop_times['departure_time'] = stop_times['departure_time'].fillna("00:00:00").apply(time_to_seconds)
    stop_times = stop_times.sort_values(by=['trip_id', 'stop_sequence'])
    stop_times['next_stop_id'] = stop_times.groupby('trip_id')['stop_id'].shift(-1)
    stop_times['next_arrival_time'] = stop_times.groupby('trip_id')['arrival_time'].shift(-1)
    stop_times['travel_time'] = stop_times['next_arrival_time'] - stop_times['departure_time']

    name_to_id = stops.dropna(subset=['stop_name']).drop_duplicates('stop_name').set_index('stop_name')['stop_id'].to_dict()
    id_to_name = stops.set_index('stop_id')['stop_name'].to_dict()
    trip_to_route = trips.set_index('trip_id')['route_id'].to_dict()
    route_info = routes.set_index('route_id')[['route_short_name', 'route_type']].to_dict(orient='index')

    edge_count = 0
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
            G.add_edge(from_stop, to_stop, weight=int(travel_time), line=line_name, mode=mode)
            edge_count += 1

    logger.info(f"🔗 {edge_count} trajets ajoutés au graphe.")

    # Ajout des correspondances simples depuis les arrêts identiques
    grouped = stop_times.groupby('stop_id').size().reset_index(name='count')
    transfer_count = 0
    for stop_id in grouped['stop_id']:
        G.add_edge(stop_id, stop_id, weight=30, line="TRANSFERT", mode="Correspondance")
        transfer_count += 1

    logger.info(f"🔁 {transfer_count} correspondances ajoutées.")
    logger.info("💾 Sauvegarde du graphe dans graphe_transport.pkl...")

    with open(GRAPH_PATH, "wb") as f:
        pickle.dump((G, name_to_id, id_to_name), f)

    logger.info("✅ Graphe construit et sauvegardé avec succès.")
    return G, name_to_id, id_to_name
