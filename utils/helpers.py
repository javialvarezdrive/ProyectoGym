# utils/helpers.py (fragmento actualizado)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def format_date(date_str):
    """Convierte una fecha con formato AAAA-MM-DD a DD/MM/AAAA."""
    if isinstance(date_str, str):
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    return date_str.strftime('%d/%m/%Y')

def generate_activity_stats(activities_df):
    if activities_df.empty:
        return None, None, None

    # Si no existe la columna 'tipos_actividad', la creamos con valor None (para evitar KeyError)
    if "tipos_actividad" not in activities_df.columns:
        activities_df["tipos_actividad"] = None

    # Función para extraer el nombre de la actividad del campo "tipos_actividad"
    def extraer_nombre(x):
        if x:
            if isinstance(x, list) and len(x) > 0:
                return x[0].get("nombre", "Actividad no definida")
            elif isinstance(x, dict):
                return x.get("nombre", "Actividad no definida")
        return "Actividad no definida"

    activities_df["tipo_nombre"] = activities_df["tipos_actividad"].apply(extraer_nombre)

    # Gráfico de pastel: distribución por tipo de actividad
    fig1 = px.pie(activities_df, names="tipo_nombre", title="Distribución por Tipo de Actividad")

    # Gráfico de barras: actividades por turno
    turno_group = activities_df.groupby("turno").size().reset_index(name="count")
    fig2 = px.bar(turno_group, x="turno", y="count", title="Actividades por Turno", color="turno")

    # Para agrupar por sección, extraemos la sección del usuario de forma segura.
    def extraer_seccion(u):
        if u and isinstance(u, dict):
            return u.get("seccion", "N/A")
        return "N/A"

    # Es posible que 'usuarios' tampoco esté en las columnas; en ese caso, se asigna "N/A"
    if "usuarios" not in activities_df.columns:
        activities_df["usuarios"] = None
    activities_df["usuario_seccion"] = activities_df["usuarios"].apply(extraer_seccion)
    seccion_group = activities_df.groupby("usuario_seccion").size().reset_index(name="count")
    fig3 = px.bar(seccion_group, x="usuario_seccion", y="count", title="Actividades por Sección", color="usuario_seccion")

    return fig1, fig2, fig3
