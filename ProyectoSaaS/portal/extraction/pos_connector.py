import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sanoyfresco.db")

def get_raw_data(limit=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM VENTAS"
    if limit:
        query += f"LIMIT {limit}"

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close

    data = [dict(row) for row in rows]
    return data