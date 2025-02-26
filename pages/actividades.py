# pages/actividades.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.auth import check_login
from utils.database import get_usuarios, get_tipos_actividad, crear_actividad, get_actividades, actualizar_actividad
from utils.helpers import format_date

def agendar_actividad():
    st.header("Agendar actividad")
    st.info("Programa una actividad sin asignar usuario. Luego podrás asignar usuarios en la pestaña 'Asignar usuarios'.")
    with st.form("form_agendar"):
        # En esta pestaña no se elige usuario; se envía usuario_id = None.
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
            res = crear_actividad(None, tipo_id, fecha.isoformat(), turno, st.session_state.user["id"], observaciones)
            if res.data:
                st.success("Actividad agendada correctamente (sin usuario asignado).")
            else:
                st.error("Error al agendar la actividad.")

def extraer_actividad(row):
    # Extrae el nombre de la actividad desde la información de tipos_actividad 
    tipo_info = row.get("tipos_actividad")
    if tipo_info:
        if isinstance(tipo_info, list) and len(tipo_info) > 0:
            return tipo_info[0].get("nombre", "Actividad no definida")
        elif isinstance(tipo_info, dict):
            return tipo_info.get("nombre", "Actividad no definida")
    return "Actividad no definida"

def asignar_usuarios():
    st.header("Asignar usuarios a actividades")
    st.info("Filtra y selecciona una actividad para asignarle un usuario.")
    
    # Rango de fechas por defecto: hoy hasta hoy + 1 mes
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
         fecha_inicio = st.date_input("Fecha Inicial", value=datetime.today(), key="asig_fecha_inicio")
    with col_a2:
         fecha_fin = st.date_input("Fecha Final", value=datetime.today() + timedelta(days=30), key="asig_fecha_fin")
    with col_a3:
         filtro_turno = st.selectbox("Turno", ["", "Mañana", "Tarde", "Noche"], key="asig_turno")
    
    filtros = {
         "fecha_inicio": fecha_inicio.isoformat(),
         "fecha_fin": fecha_fin.isoformat(),
         "turno": filtro_turno
    }
    df_acts = get_actividades(filtros)  # Todas las actividades en el rango
    
    if not df_acts.empty:
         st.subheader("Actividades en el rango seleccionado")
         datos = []
         # Construir las columnas para el listado
         for _, row in df_acts.iterrows():
              fecha_str = format_date(row["fecha"])
              turno_val = row.get("turno", "")
              actividad_nombre = extraer_actividad(row)
              # Usuarios asignados según campo usuario_id: 1 si tiene, 0 si no tiene
              num_asignados = 1 if row.get("usuario_id") is not None else 0
              datos.append({
                   "Fecha": fecha_str,
                   "Turno": turno_val,
                   "Actividad": actividad_nombre,
                   "Usuarios asignados": num_asignados
              })
         df_disp = pd.DataFrame(datos)
         st.dataframe(df_disp, use_container_width=True)
         
         # Preparar opciones del selectbox sin mostrar el ID, con label "Fecha - Turno - Actividad"
         mapping = {}
         opciones = []
         for _, row in df_acts.iterrows():
              fecha_str = format_date(row["fecha"])
              turno_val = row.get("turno", "")
              actividad_nombre = extraer_actividad(row)
              label = f"{fecha_str} - {turno_val} - {actividad_nombre}"
              mapping[label] = row.get("id")
              opciones.append(label)
         actividad_sel = st.selectbox("Seleccione la actividad a la que asignar usuario", opciones)
         actividad_id = mapping.get(actividad_sel)
         
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
              opciones_usuarios = usuarios_df.apply(lambda row: f"{row['nip']} - {row['nombre']} {row['apellidos']}", axis=1).tolist()
              usuario_sel = st.selectbox("Seleccione el usuario a asignar", opciones_usuarios)
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
         st.warning("No hay actividades en el rango seleccionado.")

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
