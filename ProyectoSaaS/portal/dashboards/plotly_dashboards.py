# ============================================================
# 🔹 Dashboards Plotly basados en datos de queries.py
# ============================================================

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from portal.loaders.queries import (
    ventas_por_categoria,
    ventas_mensuales,
    lift_asociacion_productos,
    confianza_media_categoria
)
from portal.utils.filters import MONTH_NAMES_ES

# ============================================================
# 🥧 VENTAS POR CATEGORÍA (Torta ajustada, tonos azules)
# ============================================================

def dashboard_ventas_categoria(filtros=None):
    df = ventas_por_categoria(filtros)
    if df.empty:
        return "<p class='text-muted text-center'>No hay datos disponibles.</p>"

    df = df.rename(columns={'product__section__name': 'Categoría', 'total_ventas': 'Total Ventas'})

    fig = px.pie(
        df,
        names='Categoría',
        values='Total Ventas',
        color_discrete_sequence=px.colors.sequential.Blues[::-1],
        hole=0.3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextorientation='radial'
    )
    fig.update_layout(
        template='plotly_white',
        title={'x': 0.5, 'xanchor': 'center'},
        height=420,  # 🔹 antes 550 → más compacto
        legend_title_text='Categorías',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=1.15,
            font=dict(size=11)
        ),
        margin=dict(l=30, r=30, t=60, b=30)
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ============================================================
# 📈 VENTAS MENSUALES (Gráfico de línea suave)
# ============================================================

def dashboard_ventas_mensuales(filtros=None):
    df = ventas_mensuales(filtros)
    if df.empty:
        return "<p class='text-muted text-center'>No hay datos disponibles.</p>"

    # Asegurar tipo datetime
    df['mes'] = pd.to_datetime(df['mes'])
    # Crear etiqueta en español "Mes Año"
    df['mes_label'] = df['mes'].dt.month.map(MONTH_NAMES_ES) + ' ' + df['mes'].dt.year.astype(str)

    # Mantener orden cronológico para ticks
    df = df.sort_values('mes').reset_index(drop=True)
    mes_order = df['mes_label'].tolist()
    # quitar duplicados manteniendo orden
    from collections import OrderedDict
    mes_order = list(OrderedDict.fromkeys(mes_order))

    fig = px.line(
        df,
        x='mes_label',
        y='total_ventas',
        markers=True,
        line_shape='spline',
        color_discrete_sequence=['#2563eb']
    )

    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Mes",
        yaxis_title="Total Ventas ($)",
        template="plotly_white",
        height=460,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_yaxes(tickprefix="$", showgrid=True, gridcolor="lightgrey")

    # Forzar ticks en el orden correcto con labels en español
    fig.update_xaxes(tickvals=mes_order, ticktext=mes_order, tickangle=-45)

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ============================================================
# 📊 LIFT: Asociación entre productos (barras verticales normales)
# ============================================================
def dashboard_lift_asociacion(filtros=None):
    df = lift_asociacion_productos(filtros)
    if df.empty:
        return "<p class='text-muted text-center'>No hay datos de asociaciones suficientes.</p>"

    # 🔹 Unificar pares equivalentes
    df = df[df['par'].notna() & (df['par'] != '')]
    df['par'] = df['par'].apply(lambda x: " + ".join(sorted(p.strip() for p in x.split('+'))))
    df = df.groupby('par', as_index=False)['lift'].mean()
    df = df.nlargest(10, 'lift').reset_index(drop=True)

    # 🔹 Etiqueta visible (corta)
    df['par_corto'] = df['par'].apply(lambda x: x if len(x) <= 35 else x[:35] + '...')

    # 🔹 Clave interna única (para evitar solapamiento)
    df['clave_plotly'] = [f"{i}_{x}" for i, x in enumerate(df['par_corto'])]

    import plotly.express as px
    fig = px.bar(
        df,
        x='clave_plotly',        # usamos la clave interna como eje
        y='lift',
        hover_name='par',        # muestra el nombre completo al pasar el mouse
        text='lift',
        color_discrete_sequence=['#0d6efd']
    )

    # 🔹 Mostrar solo etiqueta corta en el eje X
    fig.update_xaxes(
        tickvals=df['clave_plotly'],
        ticktext=df['par_corto'],
        tickangle=-40,
        tickfont=dict(size=10),
        automargin=True
    )

    fig.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside',
        width=0.9
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
        bargap=0.25,
        margin=dict(l=60, r=60, t=80, b=180),
        xaxis_title="Par de productos",
        yaxis_title="Valor Lift",
        title={'x': 0.5, 'xanchor': 'center'}
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')











# ============================================================
# 📊 CONFIANZA MEDIA POR CATEGORÍA (sin texto arriba)
# ============================================================

def dashboard_confianza_categoria(filtros=None):
    df = confianza_media_categoria(filtros)
    if df.empty:
        return "<p class='text-muted text-center'>No hay datos disponibles.</p>"

    fig = px.bar(
        df,
        x='categoria',
        y='confianza',
        labels={'categoria': 'Categoría', 'confianza': 'Confianza Media (%)'},
        color_discrete_sequence=['#2563eb']
    )

    fig.update_traces(text=None)
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        template="plotly_white",
        height=450,
        margin=dict(l=40, r=40, t=60, b=40),
        yaxis_title="Confianza (%)",
        xaxis_title="Categoría"
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')
