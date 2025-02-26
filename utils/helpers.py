# utils/helpers.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def format_date(date_str):
    """Convierte una fecha con formato AAAA-MM-DD a DD/MM/AAAA."""
    if isinstance(date_str, str):
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    return date_str.strftime('%d/%m/%Y')

def generate_activity_calendar(activities_df):
    """Genera un heatmap interactivo con Plotly para visualizar la distribución de actividades."""
    if activities_df.empty:
        return go.Figure()
    activities_count = activities_df.groupby(['fecha', 'turno']).size().reset_index(name='count')
    fig = px.density_heatmap(
        activities_count,
        x='fecha',
        y='turno',
        z='count',
        color_continuous_scale='Viridis',
        title='Distribución de Actividades'
    )
    fig.update_layout(xaxis_title='Fecha', yaxis_title='Turno', height=400)
    return fig

def generate_activity_stats(activities_df):
    """Genera gráficos estadísticos de actividades.
       Aplana campos anidados para usar en Plotly."""
    if activities_df.empty:
        return None, None, None

    # Extraer datos anidados en columnas simples para el tipo de actividad.
    # Se revisa si el valor es una lista (y se toma el primer elemento) o un diccionario.
    activities_df["tipo_nombre"] = activities_df["tipos_actividad"].apply(
        lambda x: x[0].get("nombre") if isinstance(x, list) and len(x) > 0 
        else (x.get("nombre") if isinstance(x, dict) and "nombre" in x 
              else "Desconocido")
    )

    # De forma similar, extraemos la sección del usuario.
    activities_df["usuario_seccion"] = activities_df["usuarios"].apply(
        lambda x: x[0].get("seccion") if isinstance(x, list) and len(x) > 0 
        else (x.get("seccion") if isinstance(x, dict) and "seccion" in x 
              else "Desconocido")
    )
    
    # Gráfico de pastel: Distribución por tipo de actividad
    fig1 = px.pie(activities_df, names="tipo_nombre", title="Distribución por Tipo de Actividad")
    
    # Gráfico de barras: Actividades por turno
    turno_group = activities_df.groupby("turno").size().reset_index(name="count")
    fig2 = px.bar(turno_group, x="turno", y="count", title="Actividades por Turno", color="turno")
    
    # Gráfico de barras: Actividades por sección
    seccion_group = activities_df.groupby("usuario_seccion").size().reset_index(name="count")
    fig3 = px.bar(seccion_group, x="usuario_seccion", y="count", title="Actividades por Sección", color="usuario_seccion")
    
    return fig1, fig2, fig3
