import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "../../data/mobility.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)  # <<== AJOUT IMPORTANT !
    return conn


# conn = sqlite3.connect("data/mobility.db")
# cursor = conn.cursor()
#
# # Index sur stop_id pour stop_times
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times (stop_id);")
#
# # Index sur trip_id pour stop_times
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times (trip_id);")
#
# # Index sur stop_name pour stops
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_stops_stop_name ON stops (stop_name);")
#
# conn.commit()
# conn.close()
