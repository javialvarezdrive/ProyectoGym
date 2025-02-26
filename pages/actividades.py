import streamlit as st


import pandas as pd

from datetime import datetime, timedelta


import plotly.express as px  # Importar Plotly Express

from utils.auth import check_login


from utils.database import get_usuarios, get_tipos_actividad, crear_actividad, get_actividades, actualizar_actividad, get_monitores


from utils.database import (


    get_usuarios,


    get_tipos_actividad,


    crear_actividad,


    get_actividades,


    actualizar_actividad,


    get_monitores


)

from utils.helpers import format_date




# ... (tus funciones extraer_nombre_actividad, agendar_actividad, asignar_usuarios) ...


def extraer_nombre_actividad(row):


    """


    Extrae el nombre de la actividad desde la información en "tipos_actividad". 


    Se maneja si se retorna como lista o diccionario.


    """


    tipo_info = row.get("tipos_actividad")


    if tipo_info:


        if isinstance(tipo_info, list) and len(tipo_info) > 0:


            return tipo_info[0].get("nombre", "Actividad no definida")


        elif isinstance(tipo_info, dict):


            return tipo_info.get("nombre", "Actividad no definida")


    return "Actividad no definida"




def dashboard_actividades():


    st.header("Dashboard de Actividades")


    st.info("Visualización de datos de actividades agendadas.")


def agendar_actividad():


    st.header("Agendar actividad")


    st.info("Programa una actividad sin asignar usuario. Luego podrás asignar usuarios en la pestaña 'Asignar usuarios'.")


    


    with st.form("form_agendar"):


        # Selección opcional de monitor:


        monitores_df = get_monitores()


        if monitores_df is not None and not monitores_df.empty:


            opciones_monitores = ["(Usar monitor logueado)"] + monitores_df.apply(lambda row: f"{row['nombre']} {row['apellidos']}", axis=1).tolist()


            monitor_sel = st.selectbox("Monitor (opcional)", options=opciones_monitores)


            if monitor_sel == "(Usar monitor logueado)":


                monitor_id = st.session_state.user["id"]


            else:


                # Buscamos el monitor por la cadena completa "nombre apellido"


                selected = monitor_sel.strip()


                fila = monitores_df[monitores_df.apply(lambda row: f"{row['nombre']} {row['apellidos']}" == selected, axis=1)]


                if not fila.empty:


                    monitor_id = fila["id"].values[0]


                else:


                    monitor_id = st.session_state.user["id"]


        else:


            monitor_id = st.session_state.user["id"]


        


        # Seleccionar tipo de actividad


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


            # Se agenda la actividad sin usuario (usuario_id = None)


            res = crear_actividad(None, tipo_id, fecha.isoformat(), turno, monitor_id, observaciones)


            if res.data:


                st.success("Actividad agendada correctamente (sin usuario asignado).")


            else:


                st.error("Error al agendar la actividad.")




    # Rango de fechas para el dashboard (puedes hacerlo seleccionable)


    fecha_inicio_dashboard = datetime.today() - timedelta(days=90)  # Últimos 90 días


    fecha_fin_dashboard = datetime.today()





    filtros_dashboard = {


        "fecha_inicio": fecha_inicio_dashboard.isoformat(),


        "fecha_fin": fecha_fin_dashboard.isoformat()


def asignar_usuarios():


    st.header("Asignar usuarios a actividades")


    st.info("Filtra y selecciona una actividad para asignarle un usuario.")


    


    # Rango de fechas por defecto: desde hoy hasta hoy + 1 mes


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


    df_actividades_dashboard = get_actividades(filtros_dashboard)





    if not df_actividades_dashboard.empty:


        # 1. Gráfico de Barras: Actividades por Tipo


        st.subheader("Actividades Agendadas por Tipo")


        # Preprocesar datos para el gráfico


        df_tipos_act = df_actividades_dashboard.copy()


        df_tipos_act['nombre_actividad'] = df_tipos_act.apply(extraer_nombre_actividad, axis=1)


        conteo_tipos = df_tipos_act['nombre_actividad'].value_counts().reset_index()


        conteo_tipos.columns = ['Tipo de Actividad', 'Cantidad']





        # Crear gráfico de barras con Plotly Express


        fig_tipos_barras = px.bar(conteo_tipos,


                                   x='Tipo de Actividad',


                                   y='Cantidad',


                                   title='Cantidad de Actividades por Tipo',


                                   labels={'Tipo de Actividad': 'Tipo', 'Cantidad': 'Número de Actividades'})


        st.plotly_chart(fig_tipos_barras, use_container_width=True)





        # ... (Aquí podrías añadir más gráficos: por turno, tendencia temporal, etc.) ...





    df_acts = get_actividades(filtros)  # Se muestran todas las actividades en ese rango


    


    if not df_acts.empty:


         st.subheader("Actividades en el rango seleccionado")


         datos = []


         for _, row in df_acts.iterrows():


              fecha_str = format_date(row["fecha"])


              turno_val = row.get("turno", "")


              actividad_nombre = extraer_nombre_actividad(row)


              num_asignados = 1 if row.get("usuario_id") is not None else 0


              datos.append({


                   "Fecha": fecha_str,


                   "Turno": turno_val,


                   "Actividad": actividad_nombre,


                   "Usuarios asignados": num_asignados


              })


         df_disp = pd.DataFrame(datos)


         st.dataframe(df_disp, use_container_width=True)


         


         # Generar opciones para seleccionar la actividad (sin mostrar el ID)


         mapping = {}


         opciones = []


         for _, row in df_acts.iterrows():


              fecha_str = format_date(row["fecha"])


              turno_val = row.get("turno", "")


              actividad_nombre = extraer_nombre_actividad(row)


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


        st.warning("No hay actividades para mostrar en el dashboard en el rango de fechas seleccionado.")





         st.warning("No hay actividades en el rango seleccionado.")



def main_wrapper():

    check_login()

    st.title("Gestión de Actividades")


    tabs = st.tabs(["Agendar actividad", "Asignar usuarios", "Dashboard de Actividades"]) # Añadimos la nueva pestaña


    tabs = st.tabs(["Agendar actividad", "Asignar usuarios"])

    with tabs[0]:


        agendar_actividad()


         agendar_actividad()

    with tabs[1]:


        asignar_usuarios()


    with tabs[2]: # Contenido de la nueva pestaña "Dashboard de Actividades"


        dashboard_actividades()





         asignar_usuarios()



if __name__ == "__main__":


    main_wrapper()
