# utils/auth.py
import streamlit as st
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

# Inicializar cliente para autenticación
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_login():
    """Verifica si el monitor ha iniciado sesión; si no, detiene la ejecución."""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Por favor inicie sesión para acceder a la aplicación.")
        st.stop()
    return st.session_state.user

def login(email, password):
    """Realiza el login del monitor mediante la API de Supabase."""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        # Después de autenticar, buscamos en la tabla 'monitores'
        monitor_response = supabase.table("monitores").select("*").eq("email", email).execute()
        if monitor_response.data:
            st.session_state.user = {
                "id": monitor_response.data[0]["id"],
                "nombre": monitor_response.data[0]["nombre"],
                "apellidos": monitor_response.data[0]["apellidos"],
                "email": email
            }
            st.session_state.logged_in = True
            return True, "Inicio de sesión exitoso"
        else:
            return False, "No se encontró información del monitor."
    except Exception as e:
        return False, f"Error en el login: {str(e)}"

def logout():
    """Cierra la sesión del monitor."""
    supabase.auth.sign_out()
    st.session_state.logged_in = False
    if 'user' in st.session_state:
        del st.session_state.user

def register_monitor(nombre, apellidos, email, password):
    """Registra a un nuevo monitor (usa la API de Supabase para auth y luego inserta en la tabla)."""
    try:
        # Crear el usuario en el sistema de autenticación 
        # (generalmente se recomienda hacer esto a través de la API o el Dashboard)
        supabase.auth.sign_up({"email": email, "password": password})
        # Insertar el monitor en la tabla
        supabase.table("monitores").insert({
            "nombre": nombre,
            "apellidos": apellidos,
            "email": email
        }).execute()
        return True, "Monitor registrado exitosamente"
    except Exception as e:
        return False, f"Error al registrar: {str(e)}"
