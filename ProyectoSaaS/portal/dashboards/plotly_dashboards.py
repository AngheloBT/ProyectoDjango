import plotly.express as px
from portal.loaders.queries import ventas_por_seccion, ventas_mensuales, lift_confianza_data
import plotly.graph_objects as go

import plotly.express as px

def dashboard_ventas_seccion():
    df = ventas_por_seccion()
    # Cambiamos nombres de columnas para mostrar en gráfico
    df = df.rename(columns={
        'product__section__name': 'Sección',
        'total_ventas': 'Total Ventas'
    })

    fig = px.bar(
        df,
        x='Sección',
        y='Total Ventas',
        text='Total Ventas',
        title='📊 Ventas por Sección',
        labels={'Total Ventas': 'Monto Total (CLP)', 'Sección': 'Sección del Producto'},
        color='Sección',
        template='plotly_white'
    )
    fig.update_layout(
        title={'x':0.5, 'xanchor':'center'},  # Centrar título
        xaxis_tickangle=-45,
        yaxis_title='Monto Total ($)',
        xaxis_title='Sección',
        uniformtext_minsize=10, uniformtext_mode='hide',
        height=450
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    return fig.to_html(full_html=False)


def dashboard_ventas_mensuales():
    df = ventas_mensuales()
    if df.empty:
        return "<p>No hay datos</p>"

    fig = px.bar(
        df,
        x='mes',
        y='total_ventas',
        title="Ventas Mensuales",
        labels={'mes': 'Mes', 'total_ventas': 'Total Ventas ($)'},
        color_discrete_sequence=['#1f77b4']  # color uniforme azul
    )

    # Mejorar diseño
    fig.update_layout(
        title={'text': "Ventas Mensuales", 'x':0.5, 'xanchor':'center'},
        xaxis_title="Mes",
        yaxis_title="Total Ventas ($)",
        template="plotly_white",
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig.update_yaxes(tickprefix="$", showgrid=True, gridcolor="lightgrey")
    
    # Mostrar todos los meses con etiquetas legibles
    fig.update_xaxes(
        showgrid=False,
        tickangle=-45,        # rota las etiquetas
        dtick="M1",           # asegura un tick por mes (si el campo es datetime)
        tickformat="%b %Y",   # formato corto Mes Año (ej: Ene 2025)
        automargin=True
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')



def dashboard_lift_confianza():
    df = lift_confianza_data()
    if df.empty:
        return "<p>No hay datos</p>"

    # Valores medios
    lift_mean = round(df['lift'].mean(), 2)
    conf_mean = round(df['confianza'].mean(), 2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Lift Medio', 'Confianza Media'],
        y=[lift_mean, conf_mean],
        text=[lift_mean, conf_mean],
        textposition='outside',   # etiquetas afuera de la barra
        marker_color=['#1f77b4', '#2ca02c'],  # azul y verde más suaves
        width=0.4
    ))

    # Mejorar diseño
    fig.update_layout(
        title={'text': "Lift y Confianza Media", 'x': 0.5, 'xanchor': 'center'},
        template="plotly_white",
        yaxis_title="Valor promedio",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig.update_yaxes(showgrid=True, gridcolor="lightgrey", zeroline=True)

    return fig.to_html(full_html=False, include_plotlyjs='cdn')

