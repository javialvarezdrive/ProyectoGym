# pages/configuracion.py
import streamlit as st
from utils.auth import check_login, register_monitor
from utils.database import get_monitores, crear_tipo_actividad, get_tipos_actividad

def main():
    user = check_login()
    st.title("Configuración del Sistema")
    tabs = st.tabs(["Gestión de Monitores", "Tipos de Actividad", "Configuración General"])
    
    with tabs[0]:
        st.header("Monitores Registrados")
        monitores_df = get_monitores()
        if not monitores_df.empty:
            st.dataframe(monitores_df[["nombre", "apellidos", "email", "created_at"]], use_container_width=True)
        st.subheader("Registrar Nuevo Monitor")
        with st.form("registro_monitor"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre")
                apellidos = st.text_input("Apellidos")
            with col2:
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                confirm = st.text_input("Confirmar Contraseña", type="password")
            if st.form_submit_button("Registrar Monitor"):
                if not all([nombre, apellidos, email, password]):
                    st.error("Todos los campos son obligatorios.")
                elif password != confirm:
                    st.error("Las contraseñas no coinciden.")
                else:
                    success, msg = register_monitor(nombre, apellidos, email, password)
                    if success:
                        st.success(msg)
                        st.experimental_rerun()
                    else:
                        st.error(msg)
                        
    with tabs[1]:
        st.header("Tipos de Actividad")
        tipos_df = get_tipos_actividad()
        if not tipos_df.empty:
            st.dataframe(tipos_df[["nombre", "descripcion"]], use_container_width=True)
        st.subheader("Añadir Nuevo Tipo de Actividad")
        with st.form("nuevo_tipo"):
            nombre_tipo = st.text_input("Nombre de la Actividad")
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Añadir"):
                if not nombre_tipo:
                    st.error("El nombre es obligatorio.")
                elif not tipos_df.empty and nombre_tipo in tipos_df["nombre"].values:
                    st.error("Ya existe ese tipo de actividad.")
                else:
                    res = crear_tipo_actividad(nombre_tipo, descripcion)
                    if res.data:
                        st.success("Tipo de actividad agregado.")
                        st.experimental_rerun()
                    else:
                        st.error("Error al agregar el tipo de actividad.")
                        
    with tabs[2]:
        st.header("Configuración General")
        st.write("Versión: 1.0.0")
        st.write(f"Monitor actual: {user['nombre']} {user['apellidos']} - {user['email']}")
        if "theme" not in st.session_state:
            st.session_state.theme = "Light"
        tema = st.selectbox("Tema Visual", ["Light", "Dark"], index=0 if st.session_state.theme=="Light" else 1)
        if tema != st.session_state.theme:
            st.session_state.theme = tema
            st.success(f"Tema cambiado a {tema}")
        st.info("La configuración se guardará temporalmente durante la sesión.")

if __name__ == "__main__":
    main()
