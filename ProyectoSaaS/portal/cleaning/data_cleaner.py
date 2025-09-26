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
    # Nuevo:
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    df['hora'] = pd.to_datetime(df['hora']).dt.time


    # --- Total coherente ---
    df['precio_total'] = df['precio_unitario'] * df['cantidad']

    # --- Mapear sección a nombres ---
    sec_map = {16: 'Hierbas', 24: 'Frutas', 53: 'Cremas', 67: 'Untables', 83: 'Verduras', 84: 'Lacteos', 115: 'Bebidas', 123: 'Organic'}

    df['seccion_nombre'] = df['id_seccion'].map(sec_map)

    # --- Quitar duplicados (si aplica) ---
    df.drop_duplicates(inplace=True)

    return df
