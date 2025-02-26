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

    # Sidebar: Si el monitor ya inició sesión se muestra su información; si no, se muestra el formulario de login
    with st.sidebar:
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            st.success(f"Sesión iniciada como: {st.session_state.user['nombre']} {st.session_state.user['apellidos']}")
            if st.button("Cerrar sesión"):
                logout()
                st.experimental_rerun()
        else:
            st.subheader("Iniciar Sesión")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                submitted = st.form_submit_button("Iniciar sesión")
                if submitted:
                    success, msg = login(email, password)
                    if success:
                        st.success(msg)
                        st.experimental_rerun()
                    else:
                        st.error(msg)

    # Mostrar la navegación si el monitor ya ha iniciado sesión
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        pages = {
            "Usuarios": "pages/usuarios.py",
            "Actividades": "pages/actividades.py",
            "Calendario": "pages/calendario.py",
            "Reportes": "pages/reportes.py",
            "Configuración": "pages/configuracion.py"
        }
        selection = st.sidebar.radio("Navegar", list(pages.keys()))
        page_file = pages[selection]
        # Leer y ejecutar el código de la página seleccionada
        with open(page_file, "r", encoding="utf8") as f:
            code = compile(f.read(), page_file, "exec")
            exec(code, globals())
    else:
        st.info("Por favor, inicie sesión para acceder al sistema.")

if __name__ == "__main__":
    main()

