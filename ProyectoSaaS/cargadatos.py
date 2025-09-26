# populate_db.py
import os
import django

# --- Configurar Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProyectoSaaS.settings")
django.setup()

# --- Importar funciones y modelos ---
from portal.extraction.pos_connector import get_raw_data
from portal.loaders.load_data import insertar_datos

# --- Leer datos del .db (limit opcional para pruebas) ---
data = get_raw_data(None)  # pon None si quieres todos los registros

# --- Insertar datos en la base de datos Django ---
insertar_datos(data)

print("✅ Datos cargados correctamente")
