from portal.models import OrderItem
from django.db.models import Sum, Count
import pandas as pd

def ventas_por_seccion():
    qs = OrderItem.objects.select_related('product', 'product__section').values(
        'product__section__name'
    ).annotate(
        total_ventas=Sum('precio_total'),
        total_cantidad=Sum('cantidad')
    ).order_by('-total_ventas')

    df = pd.DataFrame(list(qs))
    return df


def ventas_por_cliente():
    qs = OrderItem.objects.select_related('order', 'order__client').values(
        'order__client__nombre'
    ).annotate(
        total_ventas=Sum('precio_total')
    ).order_by('-total_ventas')

    df = pd.DataFrame(list(qs))
    return df

