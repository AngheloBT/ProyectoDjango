import sqlite3
import os

# DB_PATH ahora apunta al mismo directorio del script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sanoyfresco.db")

def get_raw_data(limit=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM VENTAS'
    if limit:
        query += f" LIMIT {limit}"  # espacio importante antes de LIMIT

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()  # paréntesis necesarios

    data = [dict(row) for row in rows]
    return data
