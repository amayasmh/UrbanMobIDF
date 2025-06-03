import pandas as pd
import sqlite3
import networkx as nx
import os
import pickle
from networkx.algorithms.simple_paths import shortest_simple_paths

# === Configuration ===
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "databases/mobility.db")
GRAPH_PATH = os.path.join(DATA_DIR, "graphe_transport_v0.pkl")


# === Utilitaires ===
def time_to_seconds(t):
    try:
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0


GTFS_ROUTE_TYPES = {
    0: "Tram", 1: "Métro", 2: "Train", 3: "Bus", 4: "Ferry",
    5: "Téléphérique", 6: "Funiculaire", 7: "Trolleybus", 11: "Navette"
}

# === Chargement ou création du graphe ===
if os.path.exists(GRAPH_PATH):
    with open(GRAPH_PATH, "rb") as f:
        G, name_to_id, id_to_name, stop_times = pickle.load(f)
else:
    conn = sqlite3.connect(DB_PATH)
    stops = pd.read_sql_query("SELECT * FROM stops", conn)
    stop_times = pd.read_sql_query("SELECT * FROM stop_times", conn)
    transfers = pd.read_sql_query("SELECT * FROM transfers", conn)
    trips = pd.read_sql_query("SELECT * FROM trips", conn)
    routes = pd.read_sql_query("SELECT * FROM routes", conn)
    conn.close()

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
        G.add_edge(row['from_stop_id'], row['to_stop_id'], weight=row.get('min_transfer_time', 300), line='TRANSFERT',
                   mode='Correspondance')

    with open(GRAPH_PATH, "wb") as f:
        pickle.dump((G, name_to_id, id_to_name, stop_times), f)


# === Fonctions ===
def regrouper_par_ligne(path):
    segments = []
    current_segment = []
    current_line = None
    current_mode = None

    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        edge = G.edges[a, b]
        line = edge.get('line')
        mode = edge.get('mode')

        if line != current_line or mode != current_mode:
            if current_segment:
                segments.append({"line": current_line, "mode": current_mode, "stops": current_segment})
            current_segment = [a]
            current_line = line
            current_mode = mode

        current_segment.append(b)

    if current_segment:
        segments.append({"line": current_line, "mode": current_mode, "stops": current_segment})

    return segments


def trajet_signature(path):
    signature = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        edge = G.get_edge_data(a, b)
        if edge:
            signature.append((edge.get("line"), edge.get("mode")))
    return tuple(signature)


def find_direct_trip(start_stop, end_stop):
    for trip_id, group in stop_times.groupby('trip_id'):
        stops_in_trip = list(group.sort_values('stop_sequence')['stop_id'])
        if start_stop in stops_in_trip and end_stop in stops_in_trip:
            start_index = stops_in_trip.index(start_stop)
            end_index = stops_in_trip.index(end_stop)
            if start_index < end_index:
                return stops_in_trip[start_index:end_index + 1]
    return None


# === Interface utilisateur ===
start_name = input("Station de départ : ").strip()
end_name = input("Station d'arrivée : ").strip()

if start_name not in name_to_id or end_name not in name_to_id:
    print("❌ Station non reconnue.")
else:
    start_id = name_to_id[start_name]
    end_id = name_to_id[end_name]

    direct_trip = find_direct_trip(start_id, end_id)

    if direct_trip:
        paths_to_show = [direct_trip]
    else:
        raw_paths = shortest_simple_paths(G, start_id, end_id, weight="weight")
        unique_signatures = set()
        filtered_paths = []

        for path in raw_paths:
            sig = trajet_signature(path)
            if sig in unique_signatures:
                continue
            unique_signatures.add(sig)
            filtered_paths.append(path)
            if len(filtered_paths) >= 3:
                break
        paths_to_show = filtered_paths

    for idx, path in enumerate(paths_to_show):
        segments = regrouper_par_ligne(path)
        print(f"\n🛤️ Itinéraire {idx + 1} :")

        total_time = 0
        for i, seg in enumerate(segments):
            stop_names = [id_to_name.get(sid, sid) for sid in seg['stops']]
            print(f" → Ligne {seg['mode']} {seg['line']} : {' → '.join(stop_names)}")

            for j in range(len(seg['stops']) - 1):
                edge = G.get_edge_data(seg['stops'][j], seg['stops'][j + 1])
                total_time += edge.get("weight", 0)

            if i < len(segments) - 1:
                from_stop = seg['stops'][-1]
                to_stop = segments[i + 1]['stops'][0]
                transfer_edge = G.get_edge_data(from_stop, to_stop, {})
                transfer_time = transfer_edge.get("weight", 300)
                print(
                    f" ↪️ Correspondance : {id_to_name.get(from_stop)} → {id_to_name.get(to_stop)} ({transfer_time // 60} min)")
                total_time += transfer_time

        print(f"⏱️ Temps total estimé : {int(total_time // 60)} minutes {int(total_time % 60)} secondes")
