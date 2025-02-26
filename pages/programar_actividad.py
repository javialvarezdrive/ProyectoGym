import streamlit as st
from datetime import datetime
from utils.auth import check_login
from utils.database import get_tipos_actividad, crear_actividad

def main():
    # Verifica que el monitor haya iniciado sesión
    check_login()
    st.title("Programar actividad")
    st.write("Programa una actividad sin asignar un usuario.")

    # Desplegable para seleccionar el tipo de actividad.
    # Para este ejemplo, usamos dos opciones fijas.
    activity_options = ["Defensa Personal", "Acondicionamiento Físico"]
    tipo_seleccionado = st.selectbox("Tipo de actividad", activity_options)

    # Seleccionar la fecha con un calendario
    fecha = st.date_input("Fecha", value=datetime.today())

    # Seleccionar el turno.
    turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])

    # Botón para programar la actividad
    if st.button("Programar actividad"):
        # Buscar en la tabla de tipos de actividad el id correspondiente al tipo seleccionado.
        df_tipos = get_tipos_actividad()
        try:
            tipo_actividad_id = df_tipos[df_tipos["nombre"] == tipo_seleccionado]["id"].iloc[0]
        except Exception as e:
            st.error("No se encontró el tipo de actividad en la base de datos.")
            return

        # Obtener el id del monitor que programa la actividad (el monitor que inició sesión)
        monitor_id = st.session_state.user["id"]

        # Llamar a la función para crear actividad, dejando usuario_id como None.
        result = crear_actividad(None, tipo_actividad_id, fecha.isoformat(), turno, monitor_id,
                                  observaciones="Programación sin asignación de usuario")
        if result.data:
            st.success("Actividad programada correctamente")
        else:
            st.error("Error al programar la actividad")

if __name__ == "__main__":
    main()
