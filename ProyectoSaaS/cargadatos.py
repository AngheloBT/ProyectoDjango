import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProyectoSaaS.settings")
django.setup()


from portal.extraction.pos_connector import get_raw_data
from portal.loaders.load_data import insertar_datos


data = get_raw_data(None)  # pon None si quieres todos los registros


insertar_datos(data)

print("✅ Datos cargados correctamente")
