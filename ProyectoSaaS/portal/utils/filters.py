# c:\Users\Anghelo\Documents\ProyectoSaaS\ProyectoSaaS\portal\utils\filters.py
from django.utils import timezone
from datetime import timedelta, date
from portal.models import Order
from django.db.models import Max, Min

# Diccionario global de meses en español (exportable)
MONTH_NAMES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def obtener_filtros(request):
    """
    Devuelve un diccionario con los filtros globales del dashboard.
    Añade la clave 'hay_filtros' = True|False para que la view decida pasar
    None a las consultas si no hay parámetros GET relevantes.
    """
    # Raw params (None si no vienen)
    raw_periodo = request.GET.get('periodo')
    categoria = request.GET.get('categoria')

    # por defecto mostrar mensual si no vienen filtros (para UI), pero guardamos raw_periodo
    periodo = (raw_periodo or 'mes').lower()
    
    # Captura los nombres correctos de los inputs
    fecha_dia = request.GET.get('fecha_dia')
    fecha_semana = request.GET.get('fecha_semana')
    mes_filtro = request.GET.get('mes_filtro')
    anio_filtro = request.GET.get('anio_filtro')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # Indica si hay parámetros de filtro reales en la URL
    hay_filtros = bool(
        raw_periodo or categoria or fecha_dia or fecha_semana or mes_filtro or anio_filtro or fecha_desde or fecha_hasta
    )

    # Obtener rango de fechas disponibles (BD)
    min_fecha = Order.objects.aggregate(min_fecha=Min('fecha'))['min_fecha'] or timezone.now().date()
    max_fecha = Order.objects.aggregate(max_fecha=Max('fecha'))['max_fecha'] or timezone.now().date()

    mostrar_rango = False

    try:
        # 🔹 Rango personalizado
        if periodo == 'personalizado':
            if fecha_desde and fecha_hasta:
                inicio = date.fromisoformat(fecha_desde)
                fin = date.fromisoformat(fecha_hasta)
            else:
                inicio = fin = max_fecha
            mostrar_rango = True
            subtitle = f"{inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}"

        # 🔹 Día
        elif periodo == 'dia':
            if fecha_dia:
                inicio = fin = date.fromisoformat(fecha_dia)
            else:
                inicio = fin = max_fecha
            subtitle = f"Día {inicio.strftime('%d/%m/%Y')}"

        # 🔹 Semana
        elif periodo == 'semana':
            if fecha_semana:
                inicio = date.fromisoformat(fecha_semana)
            else:
                inicio = max_fecha
            inicio -= timedelta(days=inicio.weekday())  # lunes
            fin = inicio + timedelta(days=6)
            subtitle = f"Semana {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}"

        # 🔹 Mes
        elif periodo == 'mes':
            if mes_filtro:
                # mes_filtro viene en formato YYYY-MM
                year, month = mes_filtro.split('-')
                inicio = date(int(year), int(month), 1)
            elif anio_filtro:
                inicio = date(int(anio_filtro), 1, 1)
            else:
                inicio = max_fecha.replace(day=1)
            # Fin del mes
            if inicio.month == 12:
                fin = date(inicio.year, 12, 31)
            else:
                fin = date(inicio.year, inicio.month + 1, 1) - timedelta(days=1)
            # Usar nombre del mes en español
            subtitle = f"Mes {MONTH_NAMES_ES.get(inicio.month, inicio.strftime('%B'))} {inicio.year}"

        # 🔹 Año
        elif periodo == 'anio':
            if anio_filtro:
                inicio = date(int(anio_filtro), 1, 1)
                fin = date(int(anio_filtro), 12, 31)
            else:
                inicio = max_fecha.replace(month=1, day=1)
                fin = max_fecha.replace(month=12, day=31)
            subtitle = f"Año {inicio.year}"

        else:
            inicio = fin = max_fecha
            subtitle = f"Día {inicio.strftime('%d/%m/%Y')}"

    except (ValueError, AttributeError):
        # Si hay error en la conversión, usar fecha máxima
        inicio = fin = max_fecha
        subtitle = f"Día {inicio.strftime('%d/%m/%Y')}"

    años_disponibles = list(range(min_fecha.year, max_fecha.year + 1))
    meses_disponibles = list(range(1, 13))

    # asegurar que 'mes' devuelva un string YYYY-MM si no viene explícito
    mes_value = mes_filtro if mes_filtro else inicio.strftime('%Y-%m')

    return {
        'inicio': inicio,
        'fin': fin,
        'categoria': categoria,
        'mostrar_rango': mostrar_rango,
        'subtitle': subtitle,
        'años_disponibles': años_disponibles,
        'meses_disponibles': meses_disponibles,
        'meses_nombres': MONTH_NAMES_ES,
        'periodo': periodo,
        'mes': mes_value,
        'anio': anio_filtro,
        'hay_filtros': hay_filtros,
    }