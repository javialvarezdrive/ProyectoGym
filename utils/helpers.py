# utils/helpers.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def format_date(date_str):
    if isinstance(date_str, str):
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    return date_str.strftime("%d/%m/%Y")

def generate_activity_calendar(activities_df):
    if activities_df.empty:
        return go.Figure()
    activities_count = activities_df.groupby(["fecha", "turno"]).size().reset_index(name="count")
    fig = px.density_heatmap(
        activities_count,
        x="fecha",
        y="turno",
        z="count",
        color_continuous_scale="Viridis",
        title="Distribución de Actividades"
    )
    fig.update_layout(xaxis_title="Fecha", yaxis_title="Turno", height=400)
    return fig

def generate_activity_stats(activities_df):
    if activities_df.empty:
        return None, None, None

    def extraer_tipo(tipo_info):
        if isinstance(tipo_info, list) and len(tipo_info) > 0:
            return tipo_info[0].get("nombre", "Actividad no definida")
        if isinstance(tipo_info, dict):
            return tipo_info.get("nombre", "Actividad no definida")
        return "Actividad no definida"

    activities_df["tipo_nombre"] = activities_df["tipos_actividad"].apply(extraer_tipo)

    def extraer_seccion(usuario):
        if isinstance(usuario, list) and len(usuario) > 0:
            return usuario[0].get("seccion", "N/A")
        if isinstance(usuario, dict):
            return usuario.get("seccion", "N/A")
        return "N/A"

    activities_df["usuario_seccion"] = activities_df["usuarios"].apply(extraer_seccion)

    fig1 = px.pie(activities_df, names="tipo_nombre", title="Distribución por Tipo de Actividad")
    turno_group = activities_df.groupby("turno").size().reset_index(name="count")
    fig2 = px.bar(turno_group, x="turno", y="count", title="Actividades por Turno", color="turno")
    seccion_group = activities_df.groupby("usuario_seccion").size().reset_index(name="count")
    fig3 = px.bar(seccion_group, x="usuario_seccion", y="count", title="Actividades por Sección", color="usuario_seccion")

    return fig1, fig2, fig3
