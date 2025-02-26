# pages/actividades.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px  # Importar Plotly Express
from utils.auth import check_login
from utils.database import get_usuarios, get_tipos_actividad, crear_actividad, get_actividades, actualizar_actividad, get_monitores
from utils.helpers import format_date

# ... (tus funciones extraer_nombre_actividad, agendar_actividad, asignar_usuarios) ...

def dashboard_actividades():
    st.header("Dashboard de Actividades")
    st.info("Visualización de datos de actividades agendadas.")

    # Rango de fechas para el dashboard (puedes hacerlo seleccionable)
    fecha_inicio_dashboard = datetime.today() - timedelta(days=90)  # Últimos 90 días
    fecha_fin_dashboard = datetime.today()

    filtros_dashboard = {
        "fecha_inicio": fecha_inicio_dashboard.isoformat(),
        "fecha_fin": fecha_fin_dashboard.isoformat()
    }
    df_actividades_dashboard = get_actividades(filtros_dashboard)

    if not df_actividades_dashboard.empty:
        # 1. Gráfico de Barras: Actividades por Tipo
        st.subheader("Actividades Agendadas por Tipo")
        # Preprocesar datos para el gráfico
        df_tipos_act = df_actividades_dashboard.copy()
        df_tipos_act['nombre_actividad'] = df_tipos_act.apply(extraer_nombre_actividad, axis=1)
        conteo_tipos = df_tipos_act['nombre_actividad'].value_counts().reset_index()
        conteo_tipos.columns = ['Tipo de Actividad', 'Cantidad']

        # Crear gráfico de barras con Plotly Express
        fig_tipos_barras = px.bar(conteo_tipos,
                                   x='Tipo de Actividad',
                                   y='Cantidad',
                                   title='Cantidad de Actividades por Tipo',
                                   labels={'Tipo de Actividad': 'Tipo', 'Cantidad': 'Número de Actividades'})
        st.plotly_chart(fig_tipos_barras, use_container_width=True)

        # ... (Aquí podrías añadir más gráficos: por turno, tendencia temporal, etc.) ...

    else:
        st.warning("No hay actividades para mostrar en el dashboard en el rango de fechas seleccionado.")


def main_wrapper():
    check_login()
    st.title("Gestión de Actividades")
    tabs = st.tabs(["Agendar actividad", "Asignar usuarios", "Dashboard de Actividades"]) # Añadimos la nueva pestaña
    with tabs[0]:
        agendar_actividad()
    with tabs[1]:
        asignar_usuarios()
    with tabs[2]: # Contenido de la nueva pestaña "Dashboard de Actividades"
        dashboard_actividades()


if __name__ == "__main__":
    main_wrapper()
