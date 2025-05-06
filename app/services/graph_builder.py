# fichier : app/services/graph_builder.py

import pandas as pd
import networkx as nx

def time_to_seconds(t: str) -> int:
    """Convertit HH:MM:SS en secondes"""
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

def build_graph(stops, stop_times, trips, routes, transfers):
    G = nx.DiGraph()

    stop_times_sorted = stop_times.sort_values(['trip_id', 'stop_sequence'])

    for trip_id, group in stop_times_sorted.groupby('trip_id'):
        group = group.reset_index(drop=True)
        route_row = trips[trips['trip_id'] == trip_id]
        route_id = route_row['route_id'].values[0] if not route_row.empty else None
        route_name = routes[routes['route_id'] == route_id]['route_long_name'].values[0] if route_id else ""

        for i in range(len(group) - 1):
            from_row = group.iloc[i]
            to_row = group.iloc[i + 1]

            if pd.notnull(from_row['departure_time']) and pd.notnull(to_row['arrival_time']):
                dep = time_to_seconds(from_row['departure_time'])
                arr = time_to_seconds(to_row['arrival_time'])

                G.add_edge(
                    from_row['stop_id'],
                    to_row['stop_id'],
                    weight=arr - dep,
                    type='ride',
                    trip_id=trip_id,
                    route_name=route_name
                )

    for _, row in transfers.iterrows():
        G.add_edge(
            row['from_stop_id'],
            row['to_stop_id'],
            weight=int(row['min_transfer_time']),
            type='transfer',
            route_name="Transfert"
        )

    return G
