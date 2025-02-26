# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga el archivo .env si existe

try:
    import streamlit as st
    SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
except Exception as e:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rvglsjiqpvxtdghzcvxi.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ2Z2xzamlxcHZ4dGRnaHpjdnhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1NjQzODMsImV4cCI6MjA1NjE0MDM4M30.c-4RwrKEGGQwRtEmCuXx3nERLiwJrGgcY03Qkfo69CY")

APP_NAME = "Gestión de Gimnasio"
