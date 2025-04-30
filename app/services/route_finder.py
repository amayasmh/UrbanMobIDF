import networkx as nx


def find_best_route(G, start_stop_id, start_time, end_stop_id):
    start_node = f"{start_stop_id}@{start_time}"

    # Dijkstra pour trouver le chemin le plus rapide
    try:
        path = nx.dijkstra_path(G, start_node, f"{end_stop_id}@*", weight='weight')
    except nx.NetworkXNoPath:
        return None  # Aucun itinéraire trouvé

    return path
