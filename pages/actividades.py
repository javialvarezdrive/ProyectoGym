# pages/actividades.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import check_login
from utils.database import get_usuarios, get_tipos_actividad, crear_actividad, get_actividades, actualizar_actividad
from utils.helpers import format_date

def agendar_actividad():
    st.header("Agendar actividad")
    st.info("Programa una actividad sin asignar usuario. Podrás asignar usuarios luego en la pestaña 'Asignar usuarios'.")
    with st.form("form_agendar"):
        # En esta pestaña NO se elige usuario
        tipos_df = get_tipos_actividad()
        if tipos_df.empty:
            st.error("No hay tipos de actividad definidos.")
            return
        tipo_sel = st.selectbox("Tipo de Actividad", tipos_df["nombre"].tolist())
        tipo_id = tipos_df[tipos_df["nombre"] == tipo_sel]["id"].values[0]
            
        fecha = st.date_input("Fecha", min_value=datetime.today())
        turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
        observaciones = st.text_area("Observaciones", height=100)
        
        if st.form_submit_button("Agendar actividad"):
            # Se envía usuario_id = None (sin asignación)
            res = crear_actividad(None, tipo_id, fecha.isoformat(), turno, st.session_state.user["id"], observaciones)
            if res.data:
                st.success("Actividad agendada correctamente (sin usuario asignado).")
            else:
                st.error("Error al agendar la actividad.")

def asignar_usuarios():
    st.header("Asignar usuarios a actividades")
    st.info("Filtra y selecciona una actividad sin usuario asignado para asignarle un usuario.")
    
    # Paso 1: Filtrar actividades sin usuario asignado
    st.subheader("Filtrar actividades")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        fecha_inicio = st.date_input("Fecha Inicial", key="asig_fecha_inicio")
    with col_a2:
        fecha_fin = st.date_input("Fecha Final", key="asig_fecha_fin")
    with col_a3:
        filtro_turno = st.selectbox("Turno", ["", "Mañana", "Tarde", "Noche"], key="asig_turno")
    
    filtros = {
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "turno": filtro_turno
    }
    # Obtener actividades
    df_acts = get_actividades(filtros)
    # Filtrar aquellas sin usuario asignado; suponemos que en el resultado, la columna "usuarios" es null o {}
    if not df_acts.empty:
        df_acts = df_acts[df_acts["usuarios"].isna() | (df_acts["usuarios"] == {})]
    
    if not df_acts.empty:
        st.subheader("Actividades sin usuario asignado")
        datos = []
        for _, row in df_acts.iterrows():
            actividad = (row.get("tipos_actividad") or {}).get("nombre", "Actividad")
            datos.append({
                "ID": row.get("id"),
                "Fecha": format_date(row["fecha"]),
                "Turno": row.get("turno", ""),
                "Actividad": actividad
            })
        df_disp = pd.DataFrame(datos)
        st.dataframe(df_disp, use_container_width=True)
        
        actividad_id = st.text_input("Ingrese el ID de la actividad a la que desea asignar un usuario", key="act_id")
        if actividad_id:
            st.subheader("Filtrar usuarios")
            col_u1, col_u2, col_u3, col_u4, col_u5 = st.columns(5)
            with col_u1:
                filtro_nip = st.text_input("NIP", key="filtro_nip")
            with col_u2:
                filtro_nombre = st.text_input("Nombre", key="filtro_nombre")
            with col_u3:
                filtro_apellidos = st.text_input("Apellidos", key="filtro_apellidos")
            with col_u4:
                filtro_seccion = st.selectbox("Sección", ["", "SETRA", "Motorista", "GOA", "Patrullas"], key="filtro_seccion")
            with col_u5:
                filtro_grupo = st.selectbox("Grupo", ["", "G-1", "G-2", "G-3"], key="filtro_grupo")
            
            usuarios_df = get_usuarios(activo=None)
            # Aplicar filtros a usuarios
            if filtro_nip:
                usuarios_df = usuarios_df[usuarios_df["nip"].astype(str).str.contains(filtro_nip)]
            if filtro_nombre:
                usuarios_df = usuarios_df[usuarios_df["nombre"].str.contains(filtro_nombre, case=False)]
            if filtro_apellidos:
                usuarios_df = usuarios_df[usuarios_df["apellidos"].str.contains(filtro_apellidos, case=False)]
            if filtro_seccion:
                usuarios_df = usuarios_df[usuarios_df["seccion"] == filtro_seccion]
            if filtro_grupo:
                usuarios_df = usuarios_df[usuarios_df["grupo"] == filtro_grupo]
            
            st.subheader("Usuarios filtrados")
            st.dataframe(usuarios_df, use_container_width=True)
            
            if not usuarios_df.empty:
                usuario_sel = st.selectbox("Seleccione el usuario a asignar", 
                                           usuarios_df.apply(lambda row: f"{row['nip']} - {row['nombre']} {row['apellidos']}", axis=1).tolist())
                usuario_nip = int(usuario_sel.split(" - ")[0])
                usuario_id = usuarios_df[usuarios_df["nip"] == usuario_nip]["id"].values[0]
                if st.button("Asignar usuario a la actividad"):
                    res = actualizar_actividad(actividad_id, {"usuario_id": usuario_id})
                    if res.data:
                        st.success("Usuario asignado a la actividad correctamente.")
                    else:
                        st.error("Error al asignar usuario a la actividad.")
            else:
                st.warning("No se encontraron usuarios con los filtros aplicados.")
    else:
        st.warning("No hay actividades sin usuario asignado en ese rango.")

def main():
    check_login()
    st.title("Gestión de Actividades")
    tabs = st.tabs(["Agendar actividad", "Asignar usuarios"])
    
    with tabs[0]:
        agendar_actividad()
    with tabs[1]:
        asignar_usuarios()
        
if __name__ == "__main__":
    main()
