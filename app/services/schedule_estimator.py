from datetime import timedelta
import pandas as pd
from app.services.db_connector import get_connection


def estimate_schedule(path, departure_dt, stop_times, trips, routes):
    schedule = []
    current_time = departure_dt

    # === Chargement des infos stations ===
    conn = get_connection()
    stops = pd.read_sql("SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops", conn)
    conn.close()
    stops_dict = stops.set_index("stop_id").to_dict("index")

    # === Préparation des horaires ===
    trip_lookup = stop_times.copy()
    trip_lookup['next_stop_id'] = trip_lookup.groupby('trip_id')['stop_id'].shift(-1)
    trip_lookup['next_arrival_time'] = trip_lookup.groupby('trip_id')['arrival_time'].shift(-1)
    trip_lookup = trip_lookup.dropna(subset=['next_stop_id'])

    trip_lookup = trip_lookup.merge(trips[['trip_id', 'route_id']], on='trip_id', how='left')
    trip_lookup = trip_lookup.merge(routes[['route_id', 'route_short_name', 'route_type']], on='route_id', how='left')

    for i in range(len(path) - 1):
        from_stop = path[i]
        to_stop = path[i + 1]

        match = trip_lookup[(trip_lookup['stop_id'] == from_stop) & (trip_lookup['next_stop_id'] == to_stop)]
        if match.empty:
            continue
        row = match.iloc[0]

        try:
            duration_sec = max(
                pd.to_timedelta(row['next_arrival_time']).total_seconds() -
                pd.to_timedelta(row['departure_time']).total_seconds(), 60)
        except Exception:
            duration_sec = 120

        stop_name = stops_dict.get(from_stop, {}).get("stop_name", from_stop)
        lat = stops_dict.get(from_stop, {}).get("stop_lat", None)
        lon = stops_dict.get(from_stop, {}).get("stop_lon", None)

        schedule.append({
            "from_stop": from_stop,
            "to_stop": to_stop,
            "departure_dt": current_time,
            "arrival_dt": current_time + timedelta(seconds=duration_sec),
            "duration_min": int(duration_sec // 60),
            "route_name": row.get("route_short_name", "?"),
            "mode": route_type_label(row.get("route_type")),
            "stop_name": stop_name,
            "lat": lat,
            "lon": lon,
        })

        current_time += timedelta(seconds=duration_sec)

    # === Dernier arrêt ===
    last_stop = path[-1]
    stop_name = stops_dict.get(last_stop, {}).get("stop_name", last_stop)
    lat = stops_dict.get(last_stop, {}).get("stop_lat", None)
    lon = stops_dict.get(last_stop, {}).get("stop_lon", None)

    schedule.append({
        "from_stop": last_stop,
        "to_stop": None,
        "departure_dt": current_time,
        "arrival_dt": current_time,
        "duration_min": 0,
        "route_name": "",
        "mode": "",
        "stop_name": stop_name,
        "lat": lat,
        "lon": lon,
    })

    return schedule


def route_type_label(gtfs_code):
    labels = {
        0: "Tram", 1: "Métro", 2: "Train", 3: "Bus",
        4: "Ferry", 5: "Téléphérique", 6: "Funiculaire",
        7: "Trolleybus", 11: "Navette"
    }
    return labels.get(gtfs_code, "Inconnu")
