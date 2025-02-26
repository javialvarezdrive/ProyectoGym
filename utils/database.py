# utils/database.py
from supabase import create_client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Usuarios
def get_usuarios(activo=True):
    if activo is not None:
        response = supabase.table("usuarios").select("*").eq("activo", activo).execute()
    else:
        response = supabase.table("usuarios").select("*").execute()
    return pd.DataFrame(response.data)

def get_usuario_by_nip(nip):
    response = supabase.table("usuarios").select("*").eq("nip", nip).execute()
    return response.data[0] if response.data else None

def crear_usuario(nip, nombre, apellidos, seccion, grupo):
    usuario = {
        "nip": nip,
        "nombre": nombre,
        "apellidos": apellidos,
        "seccion": seccion,
        "grupo": grupo,
        "activo": True
    }
    return supabase.table("usuarios").insert(usuario).execute()

def actualizar_usuario(id, datos):
    return supabase.table("usuarios").update(datos).eq("id", id).execute()

# Tipos de Actividad
def get_tipos_actividad():
    response = supabase.table("tipos_actividad").select("*").execute()
    return pd.DataFrame(response.data)

def crear_tipo_actividad(nombre, descripcion):
    datos = {"nombre": nombre, "descripcion": descripcion}
    return supabase.table("tipos_actividad").insert(datos).execute()

# Actividades
def get_actividades(filtros=None):
    query = supabase.table("actividades").select("""
            *,
            usuarios!inner(*),
            tipos_actividad!inner(*),
            monitores!inner(nombre, apellidos)
        """)
    if filtros:
        if "fecha_inicio" in filtros and filtros["fecha_inicio"]:
            query = query.gte("fecha", filtros["fecha_inicio"])
        if "fecha_fin" in filtros and filtros["fecha_fin"]:
            query = query.lte("fecha", filtros["fecha_fin"])
        if "turno" in filtros and filtros["turno"]:
            query = query.eq("turno", filtros["turno"])
        if "tipo_actividad" in filtros and filtros["tipo_actividad"]:
            query = query.eq("tipo_actividad_id", filtros["tipo_actividad"])
        if "seccion" in filtros and filtros["seccion"]:
            query = query.eq("usuarios->>seccion", filtros["seccion"])
        if "grupo" in filtros and filtros["grupo"]:
            query = query.eq("usuarios->>grupo", filtros["grupo"])
        if "completada" in filtros:
            query = query.eq("completada", filtros["completada"])
    response = query.execute()
    return pd.DataFrame(response.data)

def crear_actividad(usuario_id, tipo_actividad_id, fecha, turno, monitor_id, observaciones=""):
    actividad = {
        "usuario_id": usuario_id,
        "tipo_actividad_id": tipo_actividad_id,
        "fecha": fecha,
        "turno": turno,
        "monitor_id": monitor_id,
        "completada": False,
        "observaciones": observaciones
    }
    return supabase.table("actividades").insert(actividad).execute()

def actualizar_actividad(id, datos):
    return supabase.table("actividades").update(datos).eq("id", id).execute()

# Monitores
def get_monitores():
    response = supabase.table("monitores").select("*").execute()
    return pd.DataFrame(response.data)
