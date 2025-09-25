import pandas as pd
from datetime import datetime

def clean_data(raw_data):
    """
    Recibe lista de diccionarios (raw_data) desde pos_connection.get_raw_data()
    Devuelve un DataFrame limpio listo para insertar en Models Django.
    """
    # Convertir a DataFrame para manipular fácilmente
    df = pd.DataFrame(raw_data)

    # --- Limpieza de fechas y horas ---
    # Suponiendo fecha como YYYYMMDD y hora como HH:MM:SS (str o num)
    df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d').dt.date
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time

    # --- Total coherente ---
    df['precio_total'] = df['precio_unitario'] * df['cantidad']

    # --- Mapear departamento y sección a nombres ---
    dept_map = {1: 'Electrónica', 2: 'Ropa', 3: 'Hogar'}
    sec_map = {1: 'Celulares', 2: 'TV', 3: 'Camisas', 4: 'Sábanas'}

    df['departamento_nombre'] = df['id_departamento'].map(dept_map)
    df['seccion_nombre'] = df['id_seccion'].map(sec_map)

    # --- Quitar duplicados (si aplica) ---
    df.drop_duplicates(inplace=True)

    return df
