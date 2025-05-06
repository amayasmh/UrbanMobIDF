# fichier : app/services/route_finder.py

import networkx as nx
from datetime import datetime

def time_to_seconds(t: str) -> int:
    """Convertit une heure HH:MM:SS en secondes"""
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds: int) -> str:
    """Convertit des secondes en heure HH:MM:SS"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def find_best_route(G, start_stop_id, departure_time_str, end_stop_id):
    """
    Calcule le meilleur itinéraire entre deux arrêts, y compris les correspondances.

    Arguments :
    - G : graphe NetworkX construit avec build_graph()
    - start_stop_id : identifiant de l'arrêt de départ
    - departure_time_str : heure de départ souhaitée ("HH:MM:SS")
    - end_stop_id : identifiant de l'arrêt d'arrivée

    Retourne :
    - Un dict contenant le chemin, les étapes et la durée totale
    """
    start_time_sec = time_to_seconds(departure_time_str)

    if start_stop_id == end_stop_id:
        return {
            'path': [start_stop_id],
            'steps': [],
            'total_duration_min': 0
        }

    try:
        path = nx.shortest_path(G, source=start_stop_id, target=end_stop_id, weight="weight")
    except nx.NetworkXNoPath:
        return None

    steps = []
    current_time = start_time_sec
    total_duration = 0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        edge = G[u][v]
        duration = int(edge['weight'])
        arrival_time = current_time + duration

        steps.append({
            "from_stop": u,
            "to_stop": v,
            "type": edge.get("type", "unknown"),
            "route_name": edge.get("route_name", "Transfert"),
            "trip_id": edge.get("trip_id", ""),
            "departure_time": seconds_to_time(current_time),
            "arrival_time": seconds_to_time(arrival_time),
            "duration_min": duration // 60
        })

        current_time = arrival_time
        total_duration += duration

    return {
        "path": path,
        "steps": steps,
        "total_duration_min": total_duration // 60
    }
