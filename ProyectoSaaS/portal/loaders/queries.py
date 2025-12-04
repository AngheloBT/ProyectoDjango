from portal.models import OrderItem, Order, Section
from django.db.models import Sum, Max, Count
import pandas as pd
from django.utils import timezone
from datetime import timedelta
from itertools import combinations

# ============================================================
# Consultas y métricas del dashboard - compatible con filtros
# Si filtros is None -> comportamiento "original" (sin aplicar filtros GET)
# ============================================================

def get_dashboard_cards(filtros=None):
    """
    Retorna los 4 KPI principales del dashboard.
    Si filtros es None -> aplica sobre datos actuales (última fecha registrada para cálculos relativos).
    Si filtros provisto -> aplica rango y categoría.
    """
    ultima_fecha = Order.objects.aggregate(ultima=Max('fecha'))['ultima']
    hoy = ultima_fecha or timezone.now().date()
    ayer = hoy - timedelta(days=1)
    inicio_mes = hoy.replace(day=1)
    mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
    fin_mes_anterior = inicio_mes - timedelta(days=1)

    qs = OrderItem.objects.all()

    # Aplicar filtros si vienen
    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])

    # Ventas del día
    ventas_hoy = qs.filter(order__fecha=hoy).aggregate(total=Sum('precio_total'))['total'] or 0
    ventas_ayer = qs.filter(order__fecha=ayer).aggregate(total=Sum('precio_total'))['total'] or 0
    variacion_dia = ((ventas_hoy - ventas_ayer) / ventas_ayer * 100) if ventas_ayer else 0

    # Ventas del mes (relativo a hoy)
    ventas_mes = qs.filter(order__fecha__gte=inicio_mes).aggregate(total=Sum('precio_total'))['total'] or 0
    ventas_mes_anterior = qs.filter(order__fecha__range=(mes_anterior, fin_mes_anterior)).aggregate(total=Sum('precio_total'))['total'] or 0
    variacion_mes = ((ventas_mes - ventas_mes_anterior) / ventas_mes_anterior * 100) if ventas_mes_anterior else 0

    # Transacciones (se usan Orders sin filtrar por product-level qs para contar órdenes)
    trans_hoy = Order.objects.filter(fecha=hoy).count()
    trans_ayer = Order.objects.filter(fecha=ayer).count()
    variacion_trans = ((trans_hoy - trans_ayer) / trans_ayer * 100) if trans_ayer else 0

    # Productos vendidos
    prod_hoy = qs.filter(order__fecha=hoy).aggregate(total=Sum('cantidad'))['total'] or 0
    prod_ayer = qs.filter(order__fecha=ayer).aggregate(total=Sum('cantidad'))['total'] or 0
    variacion_prod = ((prod_hoy - prod_ayer) / prod_ayer * 100) if prod_ayer else 0

    return [
        {
            'titulo': 'Ventas del Día',
            'valor': ventas_hoy,
            'variacion': round(variacion_dia, 2),
            'tipo': 'dinero',
            'comparacion': 'vs Día Anterior',
            'icono': 'bi-cash-stack',
        },
        {
            'titulo': 'Ventas del Mes',
            'valor': ventas_mes,
            'variacion': round(variacion_mes, 2),
            'tipo': 'dinero',
            'comparacion': 'vs Mes Anterior',
            'icono': 'bi-calendar3',
        },
        {
            'titulo': 'Transacciones',
            'valor': trans_hoy,
            'variacion': round(variacion_trans, 2),
            'tipo': 'numero',
            'comparacion': 'vs Día Anterior',
            'icono': 'bi-cart-check',
        },
        {
            'titulo': 'Productos Vendidos',
            'valor': prod_hoy,
            'variacion': round(variacion_prod, 2),
            'tipo': 'numero',
            'comparacion': 'vs Día Anterior',
            'icono': 'bi-box-seam',
        },
    ]


def get_top_products(filtros=None, limit=5):
    """
    Top productos. Si filtros is None -> por defecto usa mes más reciente (comportamiento original).
    Si filtros provisto -> aplica rango y categoría.
    """
    qs = OrderItem.objects.select_related('product')

    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        else:
            # si filtros existe pero no rango, fallback a mes más reciente
            ultima_fecha = Order.objects.aggregate(ultima=Max('fecha'))['ultima']
            if ultima_fecha:
                inicio_mes = ultima_fecha.replace(day=1)
                qs = qs.filter(order__fecha__gte=inicio_mes)
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])
    else:
        # Sin filtros: comportamiento original -> mes más reciente
        ultima_fecha = Order.objects.aggregate(ultima=Max('fecha'))['ultima']
        if ultima_fecha:
            inicio_mes = ultima_fecha.replace(day=1)
            qs = qs.filter(order__fecha__gte=inicio_mes)

    qs = qs.values('product__name').annotate(
        total_vendidos=Sum('cantidad'),
        total_ventas=Sum('precio_total')
    ).order_by('-total_vendidos')[:limit]

    return list(qs)


def get_clientes_frecuentes(filtros=None, limit=10, min_pedidos=2):
    """
    Clientes frecuentes con resumen. Si filtros es None -> comportamiento original (usa rango relativo a hoy para métricas auxiliares).
    """
    ultima_fecha = Order.objects.aggregate(ultima=Max('fecha'))['ultima']
    hoy = ultima_fecha or timezone.now().date()
    inicio_mes = hoy.replace(day=1)

    qs = OrderItem.objects.values('order__client__id_client')

    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])

    qs = qs.annotate(
        total_pedidos=Count('order', distinct=True),
        total_gastado=Sum('precio_total'),
        ultima_compra=Max('order__fecha')
    ).filter(total_pedidos__gte=min_pedidos).order_by('-total_gastado')[:limit]

    resultado = []
    for c in qs:
        id_cliente = c['order__client__id_client']

        mes_actual = (
            OrderItem.objects.filter(order__client__id_client=id_cliente, order__fecha__gte=inicio_mes)
            .aggregate(total_mes=Sum('precio_total'))['total_mes'] or 0
        )

        ultima_fecha_compra = c['ultima_compra']
        ultima_compra_monto = (
            OrderItem.objects.filter(order__client__id_client=id_cliente, order__fecha=ultima_fecha_compra)
            .aggregate(total_ultima=Sum('precio_total'))['total_ultima'] or 0
        )

        resultado.append({
            'id_client': id_cliente,
            'total_pedidos': c['total_pedidos'],
            'total_gastado': c['total_gastado'],
            'ultima_compra': c['ultima_compra'],
            'ultima_compra_monto': ultima_compra_monto,
            'total_mes': mes_actual,
        })

    return resultado


# ============================================================
# Consultas específicas para dashboards (devuelven DataFrames)
# ============================================================

def ventas_por_categoria(filtros=None):
    """
    Ventas totales agrupadas por categoría (sección).
    Si filtros es None -> toda la serie; si filtros provisto -> aplica rango/categoría.
    """
    qs = OrderItem.objects.select_related('product', 'product__section')

    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])

    qs = qs.values('product__section__name').annotate(
        total_ventas=Sum('precio_total'),
        total_cantidad=Sum('cantidad')
    ).order_by('-total_ventas')

    df = pd.DataFrame(list(qs))
    return df


def ventas_mensuales(filtros=None):
    """
    Ventas agrupadas por mes.
    Si filtros es None -> usa toda la serie (comportamiento original).
    Si filtros provisto -> aplica rango/categoría.
    """
    qs = OrderItem.objects.values('order__fecha', 'precio_total')

    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])
    # if filtros is None -> no filtering -> toda la serie

    df = pd.DataFrame(list(qs))
    if df.empty:
        return pd.DataFrame()

    df['order__fecha'] = pd.to_datetime(df['order__fecha'])
    df['mes'] = df['order__fecha'].dt.to_period('M').dt.to_timestamp()
    df = df.groupby('mes')['precio_total'].sum().reset_index()
    df.rename(columns={'precio_total': 'total_ventas'}, inplace=True)
    return df


def lift_asociacion_productos(filtros=None):
    """
    Calcula lift entre pares de productos comprados juntos.
    Filtra filas sin soporte o con conteo 0 para evitar puntos '0' en la visualización.
    """
    qs = OrderItem.objects.values('order__id_order', 'product__name')

    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])

    df = pd.DataFrame(list(qs))
    if df.empty:
        return pd.DataFrame()

    df_cesta = df[['order__id_order', 'product__name']]
    df_agrupado = df_cesta.groupby('order__id_order')['product__name'].apply(lambda x: ','.join(x))
    df_trans = df_agrupado.str.get_dummies(sep=',')

    asociaciones = []
    # calcular soporte/ lift
    for ant, cons in combinations(df_trans.columns, 2):
        soporte_a = df_trans[ant].mean()
        soporte_c = df_trans[cons].mean()
        soporte_ac = (df_trans[ant] & df_trans[cons]).mean()
        # ignorar casos con soporte 0 para evitar divisiones por cero y ceros en la visualización
        if soporte_a > 0 and soporte_c > 0 and soporte_ac > 0:
            lift = soporte_ac / (soporte_a * soporte_c)
            asociaciones.append({'par': f"{ant} & {cons}", 'lift': round(lift, 2)})

    if not asociaciones:
        return pd.DataFrame()

    df_asoc = pd.DataFrame(asociaciones).sort_values(by='lift', ascending=False).head(10)
    return df_asoc


def confianza_media_categoria(filtros=None):
    """
    Calcula confianza media (probabilidad de compra conjunta) por categoría.
    Se descartan grupos con un solo producto (no aportan a confianza).
    """
    qs = OrderItem.objects.values('order__id_order', 'product__section__name', 'product__name')

    if filtros:
        if filtros.get('inicio') and filtros.get('fin'):
            qs = qs.filter(order__fecha__range=(filtros['inicio'], filtros['fin']))
        if filtros.get('categoria'):
            qs = qs.filter(product__section__id_section=filtros['categoria'])

    df = pd.DataFrame(list(qs))
    if df.empty:
        return pd.DataFrame()

    df_cesta = df.groupby(['order__id_order', 'product__section__name'])['product__name'].apply(list).reset_index()

    resultados = []
    for _, row in df_cesta.iterrows():
        n = len(row['product__name'])
        if n > 1:
            # confianza simple: proporción de productos comprados junto al menos con otro
            conf = round((n - 1) / n * 100, 2)
            resultados.append({'categoria': row['product__section__name'], 'confianza': conf})

    if not resultados:
        return pd.DataFrame()

    df_conf = pd.DataFrame(resultados)
    df_conf = df_conf.groupby('categoria')['confianza'].mean().reset_index()
    return df_conf

def get_ventas_recientes(limit=10):
    """
    Obtiene las ventas recientes del último día registrado en la BD.
    NO recibe filtros - siempre muestra comportamiento "original".
    Retorna lista de dicts con: producto, cantidad, total.
    """
    ultima_fecha = Order.objects.aggregate(ultima=Max('fecha'))['ultima']
    
    if not ultima_fecha:
        return []
    
    # Traer ventas del último día
    qs = OrderItem.objects.filter(order__fecha=ultima_fecha).select_related('product').values(
        'product__name',
        'cantidad',
        'precio_total'
    ).order_by('-precio_total')[:limit]
    
    resultado = []
    for item in qs:
        resultado.append({
            'producto': item['product__name'],
            'cantidad': item['cantidad'],
            'total': item['precio_total'],
        })
    
    return resultado