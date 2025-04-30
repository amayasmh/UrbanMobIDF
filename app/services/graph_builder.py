import networkx as nx


def build_graph(stops, stop_times, trips, routes, transfers):
    G = nx.DiGraph()

    # Lier les stops par les trajets
    for trip_id, group in stop_times.groupby('trip_id'):
        sorted_group = group.sort_values('stop_sequence')
        previous_stop = None
        previous_departure = None

        for idx, row in sorted_group.iterrows():
            stop_id = row['stop_id']
            arrival_time = row['arrival_time']
            departure_time = row['departure_time']

            node_id = f"{stop_id}@{departure_time}"
            G.add_node(node_id, stop_id=stop_id, trip_id=trip_id, time=departure_time)

            if previous_stop:
                # Arête entre deux arrêts successifs sur le même trip
                prev_node_id = f"{previous_stop}@{previous_departure}"
                G.add_edge(prev_node_id, node_id, weight=time_difference(previous_departure, arrival_time), type="ride")

            previous_stop = stop_id
            previous_departure = departure_time

    # Ajouter les correspondances (transfers)
    for idx, row in transfers.iterrows():
        from_stop = row['from_stop_id']
        to_stop = row['to_stop_id']
        min_transfer_time = row['min_transfer_time']

        # Connexion générique : permet de changer d'arrêt avec un temps d'attente
        G.add_edge(f"{from_stop}@*", f"{to_stop}@*", weight=min_transfer_time / 60, type="transfer")

    return G


def time_difference(start, end):
    h1, m1, s1 = map(int, start.split(':'))
    h2, m2, s2 = map(int, end.split(':'))
    return ((h2 * 3600 + m2 * 60 + s2) - (h1 * 3600 + m1 * 60 + s1)) / 60  # minutes
