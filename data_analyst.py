import sqlite3
import pandas as pd
from itertools import combinations

import dash
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# CARGA DE DATOS
# -------------------------
conexion = sqlite3.connect('sanoyfresco.db')
df = pd.read_sql_query("SELECT * FROM tickets", conexion)
conexion.close()

# Convertir fecha a datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# Preparar DataFrame de transacciones
df_cesta = df[['id_pedido','nombre_producto']]
df_agrupado = df_cesta.groupby('id_pedido')['nombre_producto'].apply(lambda producto: ','.join(producto))
df_transacciones = df_agrupado.str.get_dummies(sep=',')

# -------------------------
# MÉTRICAS DE REGLAS DE ASOCIACIÓN
# -------------------------
def confianza(antecedente, consecuente):
    conjunto_ac = df_transacciones[(df_transacciones[antecedente] == 1) &
                                    (df_transacciones[consecuente] == 1)]
    return len(conjunto_ac) / df_transacciones[antecedente].sum()

def lift(antecedente, consecuente):
    soporte_a = df_transacciones[antecedente].mean()
    soporte_c = df_transacciones[consecuente].mean()
    conteo_ac = len(df_transacciones[(df_transacciones[antecedente] == 1) &
                                    (df_transacciones[consecuente] == 1)])
    soporte_ac = conteo_ac / len(df_transacciones)
    return soporte_ac / (soporte_a * soporte_c)

# Generar asociaciones
umbral_confianza = 0.05
asociaciones = []

for antecedente, consecuente in combinations(df_transacciones.columns, 2):
    soporte_a = df_transacciones[antecedente].mean()
    conf = confianza(antecedente, consecuente)
    if conf > umbral_confianza:
        asociaciones.append({
            'antecedente': antecedente,
            'consecuente': consecuente,
            'soporte_a': round(soporte_a * 100,1),
            'confianza': round(conf * 100,1),
            'lift': round(lift(antecedente, consecuente),1)
        })

df_asociaciones = pd.DataFrame(asociaciones)

# -------------------------
# ENRIQUECIMIENTO DE DATOS
# -------------------------
productos_unicos = df[['id_producto', 'id_seccion', 'id_departamento', 'nombre_producto']].drop_duplicates()
df_asociaciones_enriquecido = df_asociaciones.merge(
    productos_unicos, left_on='antecedente', right_on='nombre_producto', how='left'
).drop(columns=['nombre_producto'])
df_asociaciones_enriquecido.columns = [
    'antecedente', 'consecuente', 'soporte_a', 'confianza', 'lift',
    'id_producto_a', 'id_seccion_a', 'id_departamento_a'
]

# -------------------------
# MÉTRICAS DE VENTAS
# -------------------------
df['mes'] = df['fecha'].dt.to_period('M').dt.to_timestamp()
ventas_mensuales = df.groupby('mes')['precio_total'].sum().reset_index()
ventas_promedio_pedido = df.groupby('id_pedido')['precio_total'].mean().reset_index()
total_ventas = df['precio_total'].sum()
usuarios_totales = df['id_cliente'].nunique()

# -------------------------
# DASHBOARD CON DASH
# -------------------------
app = dash.Dash(__name__)

# Dropdown para filtrar por sección
secciones = df['id_seccion'].unique()
dropdown_seccion = dcc.Dropdown(
    options=[{'label': s, 'value': s} for s in secciones],
    value=None,
    placeholder="Filtrar por sección"
)

# Gráficos
fig_ventas_mensuales = px.bar(
    ventas_mensuales, x='mes', y='precio_total',
    labels={'precio_total': 'Ventas Totales', 'mes': 'Mes'},
    title='Ventas Mensuales'
)

fig_lift_confianza = go.Figure()
fig_lift_confianza.add_trace(go.Bar(
    x=['Lift Medio', 'Confianza Media'],
    y=[df_asociaciones_enriquecido['lift'].mean(),
    df_asociaciones_enriquecido['confianza'].mean()],
    text=[round(df_asociaciones_enriquecido['lift'].mean(),2),
        round(df_asociaciones_enriquecido['confianza'].mean(),2)],
    textposition='auto',
    marker_color=['blue','green']
))
fig_lift_confianza.update_layout(title='Lift y Confianza Media')

# Tabla de asociaciones
tabla_asociaciones = dash_table.DataTable(
    data=df_asociaciones_enriquecido.to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_asociaciones_enriquecido.columns],
    page_size=10,
    style_table={'overflowX': 'auto'}
)

# Layout
app.layout = html.Div([
    html.H1("Dashboard de Ventas y Reglas de Asociación"),
    html.Div([
        html.P(f"Total de ventas: {total_ventas:.2f}"),
        html.P(f"Usuarios totales: {usuarios_totales}"),
    ]),
    html.H2("Filtrar por Sección de Producto"),
    dropdown_seccion,
    dcc.Graph(figure=fig_ventas_mensuales),
    dcc.Graph(figure=fig_lift_confianza),
    html.H2("Reglas de Asociación"),
    tabla_asociaciones
])

if __name__ == '__main__':
    app.run(debug=True)
