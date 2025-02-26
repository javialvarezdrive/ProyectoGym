# pages/reportes.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from utils.auth import check_login
from utils.database import get_actividades
from utils.helpers import generate_activity_stats

def main():
    check_login()
    st.title("Reportes y Estadísticas")
    with st.expander("Filtros de Reporte", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha Inicial", value=datetime.today()-timedelta(days=30))
        with col2:
            fecha_fin = st.date_input("Fecha Final", value=datetime.today())
        col3, col4, col5 = st.columns(3)
        with col3:
            seccion = st.selectbox("Sección", options=["Todas", "SETRA", "Motorista", "GOA", "Patrullas"])
        with col4:
            grupo = st.selectbox("Grupo", options=["Todos", "G-1", "G-2", "G-3"])
        with col5:
            completada = st.selectbox("Estado", options=["Todas", "Completadas", "Pendientes"])
    
    filtros = {"fecha_inicio": fecha_inicio.isoformat(), "fecha_fin": fecha_fin.isoformat()}
    if seccion != "Todas":
        filtros["seccion"] = seccion
    if grupo != "Todos":
        filtros["grupo"] = grupo
    if completada != "Todas":
        filtros["completada"] = True if completada=="Completadas" else False
        
    df = get_actividades(filtros)
    if not df.empty:
        st.header("Resumen General")
        total = len(df)
        comp = len(df[df["completada"]==True])
        pend = total - comp
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Actividades", total)
        col2.metric("Completadas", comp)
        col3.metric("Pendientes", pend)
        
        st.header("Estadísticas")
        fig1, fig2, fig3 = generate_activity_stats(df)
        if fig1: st.plotly_chart(fig1, use_container_width=True)
        if fig2: st.plotly_chart(fig2, use_container_width=True)
        if fig3: st.plotly_chart(fig3, use_container_width=True)
        
        st.header("Evolución Temporal")
        df["fecha"] = pd.to_datetime(df["fecha"])
        timeline = df.groupby(df["fecha"].dt.date).size().reset_index(name="count")
        fig_timeline = px.line(timeline, x="fecha", y="count", title="Evolución de Actividades")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        st.header("Exportar Datos")
        export_df = pd.DataFrame()
        export_df["NIP"] = df["usuarios"].apply(lambda x: x.get("nip") if isinstance(x, dict) else "N/A")
        export_df["Nombre"] = df["usuarios"].apply(lambda x: f"{x.get('nombre','')}" if isinstance(x, dict) else "N/A")
        export_df["Sección"] = df["usuarios"].apply(lambda x: x.get("seccion") if isinstance(x, dict) else "N/A")
        export_df["Grupo"] = df["usuarios"].apply(lambda x: x.get("grupo") if isinstance(x, dict) else "N/A")
        export_df["Fecha"] = df["fecha"].apply(lambda x: x.strftime("%Y-%m-%d"))
        export_df["Turno"] = df["turno"]
        export_df["Actividad"] = df["tipos_actividad"].apply(lambda x: x.get("nombre") if isinstance(x, dict) else "N/A")
        export_df["Completada"] = df["completada"].apply(lambda x: "Sí" if x else "No")
        csv = export_df.to_csv(index=False)
        st.download_button("Descargar CSV", data=csv, file_name="actividades.csv", mime="text/csv")
    else:
        st.warning("No hay datos para mostrar.")

if __name__ == "__main__":
    main()
