# pages/actividades.py
import streamlit as st
from datetime import datetime
from utils.auth import check_login
from utils.database import get_usuarios, get_tipos_actividad, crear_actividad, get_actividades, actualizar_actividad
from utils.helpers import format_date

def main():
    check_login()
    st.title("Gestión de Actividades")
    tabs = st.tabs(["Agendar Actividad", "Listado de Actividades"])
    
    with tabs[0]:
        st.header("Agendar Actividad")
        with st.form("form_agendar"):
            col1, col2 = st.columns(2)
            with col1:
                usuarios_df = get_usuarios()
                if not usuarios_df.empty:
                    opciones = [f"{row['nip']} - {row['nombre']} {row['apellidos']}" for _,row in usuarios_df.iterrows()]
                    usuario_sel = st.selectbox("Usuario", opciones)
                    usuario_nip = int(usuario_sel.split(" - ")[0])
                    usuario_id = usuarios_df[usuarios_df['nip']==usuario_nip]['id'].values[0]
                else:
                    st.error("No hay usuarios disponibles.")
                    usuario_id = None
                tipos_df = get_tipos_actividad()
                if not tipos_df.empty:
                    tipo_sel = st.selectbox("Tipo de Actividad", tipos_df['nombre'].tolist())
                    tipo_id = tipos_df[tipos_df['nombre']==tipo_sel]['id'].values[0]
                else:
                    st.error("No hay tipos de actividad definidos.")
                    tipo_id = None
            with col2:
                fecha = st.date_input("Fecha", min_value=datetime.today())
                turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
                observaciones = st.text_area("Observaciones", height=100)
            if st.form_submit_button("Agendar"):
                if usuario_id and tipo_id:
                    res = crear_actividad(usuario_id, tipo_id, fecha.isoformat(), turno, st.session_state.user["id"], observaciones)
                    if res.data:
                        st.success("Actividad agendada correctamente")
                    else:
                        st.error("Error al agendar actividad")
    
    with tabs[1]:
        st.header("Listado de Actividades")
        # Se pueden aplicar filtros similares (por fecha, turno, etc.)
        filtros = {}
        col1, col2, col3 = st.columns(3)
        with col1:
            fi = st.date_input("Fecha Inicial")
            filtros["fecha_inicio"] = fi.isoformat()
        with col2:
            ff = st.date_input("Fecha Final")
            filtros["fecha_fin"] = ff.isoformat()
        with col3:
            filtros["turno"] = st.selectbox("Turno", ["", "Mañana", "Tarde", "Noche"])
        df_acts = get_actividades(filtros)
        if not df_acts.empty:
            datos = []
            for _, row in df_acts.iterrows():
                datos.append({
                    "Fecha": format_date(row["fecha"]),
                    "Turno": row["turno"],
                    "Usuario": f"{row['usuarios']['nip']} - {row['usuarios']['nombre']} {row['usuarios']['apellidos']}",
                    "Actividad": row['tipos_actividad']['nombre'],
                    "Monitor": f"{row['monitores']['nombre']} {row['monitores']['apellidos']}",
                    "Completada": "Sí" if row["completada"] else "No"
                })
            st.dataframe(pd.DataFrame(datos), use_container_width=True)
        else:
            st.warning("No hay actividades que coincidan con los filtros")
                
if __name__ == "__main__":
    main()
