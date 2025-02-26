# pages/usuarios.py
import streamlit as st
import pandas as pd
from utils.auth import check_login
from utils.database import get_usuarios, crear_usuario, actualizar_usuario, get_usuario_by_nip

def main():
    check_login()
    st.title("Gestión de Usuarios del Gimnasio")
    tabs = st.tabs(["Listar Usuarios", "Nuevo Usuario", "Editar Usuario"])
    
    with tabs[0]:
        st.header("Lista de Usuarios")
        filtro_estado = st.selectbox("Mostrar:", ["Activos", "Inactivos", "Todos"])
        filtro_seccion = st.selectbox("Filtrar por Sección:", ["Todas", "SETRA", "Motorista", "GOA", "Patrullas"])
        activo = True if filtro_estado=="Activos" else False if filtro_estado=="Inactivos" else None
        df = get_usuarios(activo)
        if filtro_seccion!="Todas":
            df = df[df["seccion"]==filtro_seccion]
        if not df.empty:
            st.dataframe(df[["nip", "nombre", "apellidos", "seccion", "grupo"]], use_container_width=True)
            st.success(f"Total de usuarios: {len(df)}")
        else:
            st.warning("No se encontraron usuarios.")
    
    with tabs[1]:
        st.header("Registrar Nuevo Usuario")
        with st.form("registro_usuario"):
            col1, col2 = st.columns(2)
            with col1:
                nip = st.number_input("NIP", min_value=1, step=1)
                nombre = st.text_input("Nombre")
                apellidos = st.text_input("Apellidos")
            with col2:
                seccion = st.selectbox("Sección", ["SETRA", "Motorista", "GOA", "Patrullas"])
                grupo = st.selectbox("Grupo", ["G-1", "G-2", "G-3"])
            if st.form_submit_button("Registrar"):
                if get_usuario_by_nip(nip):
                    st.error(f"Ya existe un usuario con NIP {nip}")
                else:
                    response = crear_usuario(nip, nombre, apellidos, seccion, grupo)
                    if response.data:
                        st.success("Usuario registrado correctamente")
                    else:
                        st.error("Error al registrar el usuario")
    
    with tabs[2]:
        st.header("Editar Usuario")
        nip_busqueda = st.number_input("Ingrese NIP del usuario", min_value=1, step=1)
        if st.button("Buscar"):
            usuario = get_usuario_by_nip(nip_busqueda)
            if usuario:
                st.success(f"Usuario encontrado: {usuario['nombre']} {usuario['apellidos']}")
                with st.form("editar_usuario"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre_edit = st.text_input("Nombre", value=usuario['nombre'])
                        apellidos_edit = st.text_input("Apellidos", value=usuario['apellidos'])
                    with col2:
                        seccion_edit = st.selectbox("Sección", ["SETRA", "Motorista", "GOA", "Patrullas"],
                                                    index=["SETRA", "Motorista", "GOA", "Patrullas"].index(usuario['seccion']))
                        grupo_edit = st.selectbox("Grupo", ["G-1", "G-2", "G-3"],
                                                  index=["G-1", "G-2", "G-3"].index(usuario['grupo']))
                        estado_edit = st.selectbox("Estado", ["Activo", "Inactivo"], index=0 if usuario["activo"] else 1)
                    if st.form_submit_button("Guardar Cambios"):
                        nuevos = {"nombre": nombre_edit, "apellidos": apellidos_edit,
                                  "seccion": seccion_edit, "grupo": grupo_edit, "activo": estado_edit=="Activo"}
                        res = actualizar_usuario(usuario["id"], nuevos)
                        if res:
                            st.success("Usuario actualizado")
                        else:
                            st.error("Error al actualizar")
            else:
                st.warning("No se encontró usuario con ese NIP")
                
if __name__ == "__main__":
    main()
