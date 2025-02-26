# app.py
import streamlit as st
from utils.auth import login, logout
from config import APP_NAME

st.set_page_config(
    page_title=APP_NAME,
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title(f"🏋️ {APP_NAME}")
    
    with st.sidebar:
        if "logged_in" in st.session_state and st.session_state.logged_in:
            st.success(f"Sesión iniciada: {st.session_state.user['nombre']} {st.session_state.user['apellidos']}")
            if st.button("Cerrar sesión"):
                logout()
                st.rerun()
        else:
            st.subheader("Iniciar sesión")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Iniciar sesión"):
                    success, msg = login(email, password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                        
    if "logged_in" in st.session_state and st.session_state.logged_in:
        pages = {
            "Usuarios": "pages/usuarios.py",
            "Actividades": "pages/actividades.py",
            "Calendario": "pages/calendario.py",
            "Reportes": "pages/reportes.py",
            "Configuración": "pages/configuracion.py",
            "Programar actividad": "pages/programar_actividad.py"
        }
        selection = st.sidebar.radio("Navegar", list(pages.keys()))
        page_file = pages[selection]
        with open(page_file, "r", encoding="utf8") as f:
            code = compile(f.read(), page_file, "exec")
            exec(code, globals())
    else:
        st.info("Por favor, inicie sesión para acceder al sistema.")

if __name__ == "__main__":
    main()
