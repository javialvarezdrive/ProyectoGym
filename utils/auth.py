# utils/auth.py
import streamlit as st
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Por favor, inicie sesión para acceder a la aplicación.")
        st.stop()
    return st.session_state.user

def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        monitor_response = supabase.table("monitores").select("*").eq("email", email).execute()
        if monitor_response.data:
            st.session_state.user = {
                "id": monitor_response.data[0]["id"],
                "nombre": monitor_response.data[0]["nombre"],
                "apellidos": monitor_response.data[0]["apellidos"],
                "email": email
            }
            st.session_state.logged_in = True
            return True, "Inicio de sesión exitoso."
        else:
            return False, "No se encontró información del monitor."
    except Exception as err:
        return False, str(err)

def logout():
    supabase.auth.sign_out()
    st.session_state.logged_in = False
    if "user" in st.session_state:
        del st.session_state.user
