# fichier: app/services/graph_builder.py

import os
import pickle
import logging
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
    except Exception:
        return 0


def build_graph(stops, stop_times, trips, routes, transfers=None):
    if os.path.exists(GRAPH_PATH):
        logger.info("📦 Chargement du graphe depuis graphe_transport.pkl...")
        with open(GRAPH_PATH, "rb") as f:
            return pickle.load(f)

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
    last_mode_by_stop = {}

    for _, row in stop_times.dropna(subset=['next_stop_id']).iterrows():
        from_stop = row['stop_id']
        to_stop = row['next_stop_id']
        travel_time = row['travel_time']
        trip_id = row['trip_id']
        route_id = trip_to_route.get(trip_id)
        route = route_info.get(route_id, {})
        line_name = route.get('route_short_name', '??')
        mode = GTFS_ROUTE_TYPES.get(route.get('route_type'), '??')

        previous_mode = last_mode_by_stop.get(from_stop)
        penalty = 120 if previous_mode and previous_mode != mode else 0

        mode_penalties = {
            "Train": 1.0,
            "Métro": 1.0,
            "Tram": 1.1,
            "Bus": 1.5,
            "Trolleybus": 1.5,
            "Navette": 1.7,
            "Correspondance": 2.0
        }

        penalty_factor = mode_penalties.get(mode, 1.2)
        total_weight = int(travel_time * penalty_factor) + penalty

        if travel_time >= 0:
            G.add_edge(from_stop, to_stop, weight=total_weight, line=line_name, mode=mode)
            last_mode_by_stop[from_stop] = mode
            edge_count += 1

    logger.info(f"🔗 {edge_count} trajets ajoutés au graphe.")

    transfer_count = 0
    if transfers is not None and not transfers.empty:
        for _, row in transfers.iterrows():
            from_stop = row['from_stop_id']
            to_stop = row['to_stop_id']
            transfer_time = int(row.get('min_transfer_time', 300))
            G.add_edge(
                from_stop,
                to_stop,
                weight=int(transfer_time),
                line="TRANSFERT",
                mode="Correspondance",
                transfer_time=int(transfer_time)  # 👈 Ajout explicite
            )
            transfer_count += 1

        logger.info(f"🔁 {transfer_count} correspondances ajoutées depuis transfers.txt")
    else:
        logger.warning("⚠️ transfers.txt non fourni ou vide — aucune correspondance ajoutée")

    G.remove_edges_from([(n, n) for n in G.nodes if G.has_edge(n, n)])

    logger.info("💾 Sauvegarde du graphe dans graphe_transport.pkl...")
    with open(GRAPH_PATH, "wb") as f:
        pickle.dump((G, name_to_id, id_to_name), f)

    logger.info("✅ Graphe construit et sauvegardé avec succès.")
    return G, name_to_id, id_to_name
