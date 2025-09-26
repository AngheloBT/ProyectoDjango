import plotly.express as px
from portal.loaders.queries import ventas_por_seccion, ventas_por_cliente

def dashboard_ventas_seccion():
    df = ventas_por_seccion()
    fig = px.bar(df, x='product__section__name', y='total_ventas', 
                 title="Ventas por Sección", text='total_ventas')
    return fig.to_html(full_html=False)

def dashboard_ventas_cliente():
    df = ventas_por_cliente()
    fig = px.bar(df, x='order__client__nombre', y='total_ventas', 
                 title="Ventas por Cliente", text='total_ventas')
    return fig.to_html(full_html=False)
