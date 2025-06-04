# fichier : app/services/route_finder.py (mise à jour avec intégration IA + CO2)

import networkx as nx
import heapq

# Coûts d'émission CO2 par mode de transport (en g/km estimés)
CO2_PER_KM = {
    "Train": 15,
    "Métro": 10,
    "Tram": 8,
    "Bus": 104,
    "Trolleybus": 80,
    "Navette": 120,
    "Correspondance": 0  # pas de transport effectif
}

# Fonction de dijkstra pondérée par CO2

def find_best_path(G, start, end, alpha=1.0, beta=0.02):
    """
    alpha : poids du temps
    beta : poids de l'empreinte carbone
    """
    queue = [(0, start, [])]
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == end:
            return path

        for neighbor in G.successors(node):
            edge = G[node][neighbor]
            time_weight = edge.get("weight", 60)
            mode = edge.get("mode", "Bus")
            co2_factor = CO2_PER_KM.get(mode, 100)
            co2_weight = co2_factor * 0.3  # valeur fixe estimée car pas de distance réelle
            new_cost = cost + alpha * time_weight + beta * co2_weight
            heapq.heappush(queue, (new_cost, neighbor, path))

    return None