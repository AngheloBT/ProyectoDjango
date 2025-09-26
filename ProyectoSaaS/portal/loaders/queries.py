from portal.models import OrderItem
from django.db.models import Sum, Count
import pandas as pd
from django.utils import timezone
from datetime import timedelta


def ventas_por_seccion():
    qs = OrderItem.objects.select_related('product', 'product__section').values(
        'product__section__name'
    ).annotate(
        total_ventas=Sum('precio_total'),
        total_cantidad=Sum('cantidad')
    ).order_by('-total_ventas')

    df = pd.DataFrame(list(qs))
    return df

def ventas_mensuales():
    qs = OrderItem.objects.values('order__fecha').annotate(total_ventas=Sum('precio_total'))
    df = pd.DataFrame(list(qs))
    if not df.empty:
        df['order__fecha'] = pd.to_datetime(df['order__fecha'])
        df['mes'] = df['order__fecha'].dt.to_period('M').dt.to_timestamp()
        df = df.groupby('mes')['total_ventas'].sum().reset_index()
    return df

def lift_confianza_data():
    df = pd.DataFrame(list(OrderItem.objects.values(
        'order__id_order', 
        'product__name', 
        'product__section__id_section', 
        'product__section__departament__id_departament',
        'precio_total'
    )))
    if df.empty:
        return pd.DataFrame()
    
    # Preparar DataFrame de transacciones (uno por pedido)
    df_cesta = df[['order__id_order','product__name']]
    df_agrupado = df_cesta.groupby('order__id_order')['product__name'].apply(lambda x: ','.join(x))
    df_transacciones = df_agrupado.str.get_dummies(sep=',')
    
    # Calcular lift y confianza entre productos
    from itertools import combinations
    asociaciones = []
    umbral_confianza = 0.05
    for ant, cons in combinations(df_transacciones.columns, 2):
        soporte_a = df_transacciones[ant].mean()
        conf = len(df_transacciones[(df_transacciones[ant]==1) & (df_transacciones[cons]==1)]) / df_transacciones[ant].sum()
        if conf > umbral_confianza:
            conteo_ac = len(df_transacciones[(df_transacciones[ant]==1) & (df_transacciones[cons]==1)])
            soporte_c = df_transacciones[cons].mean()
            soporte_ac = conteo_ac / len(df_transacciones)
            lift = soporte_ac / (soporte_a * soporte_c) if soporte_a*soporte_c != 0 else 0
            asociaciones.append({'antecedente': ant, 'consecuente': cons, 'lift': round(lift,2), 'confianza': round(conf*100,2), 'soporte_a': round(soporte_a*100,2)})
    return pd.DataFrame(asociaciones)