import logging

import networkx as nx

logger = logging.getLogger(__name__)

def find_best_path(graph, start_stop_id, end_stop_id):
    try:
        path = nx.shortest_path(graph, source=start_stop_id, target=end_stop_id, weight="weight")
        logger.info(f"Chemin trouvé entre {start_stop_id} et {end_stop_id} : {path}")
        return path
    except nx.NetworkXNoPath:
        logger.warning(f"Aucun chemin trouvé entre {start_stop_id} et {end_stop_id}")
        return None
    except nx.NodeNotFound as e:
        logger.error(f"Nœud introuvable : {e}")
        return None
