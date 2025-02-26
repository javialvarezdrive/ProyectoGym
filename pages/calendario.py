# pages/calendario.py
import streamlit as st
from datetime import datetime, timedelta
from utils.auth import check_login
from utils.database import get_actividades
from utils.helpers import generate_activity_calendar, format_date
from streamlit_calendar import calendar

def main():
    check_login()
    st.title("Calendario de Actividades")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mes = st.selectbox("Mes", list(range(1, 13)), index=datetime.now().month - 1)
    with col2:
        año = st.selectbox("Año", list(range(datetime.now().year - 1, datetime.now().year + 3)), index=1)
    with col3:
        vista = st.selectbox("Vista", ["Mensual", "Semanal", "Diaria"])
    
    if vista == "Mensual":
        fecha_inicio = datetime(año, mes, 1)
        if mes < 12:
            fecha_fin = datetime(año, mes + 1, 1) - timedelta(days=1)
        else:
            fecha_fin = datetime(año + 1, 1, 1) - timedelta(days=1)
    elif vista == "Semanal":
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = fecha_inicio + timedelta(days=6)
    else:
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = fecha_inicio
    
    filtros = {
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat()
    }
    
    df = get_actividades(filtros)
    if not df.empty:
        eventos = []
        for _, row in df.iterrows():
            fecha_str = format_date(row["fecha"])
            turno = row.get("turno", "")
            # Extraer nombre de actividad
            actividad = ""
            tipo_info = row.get("tipos_actividad")
            if tipo_info:
                if isinstance(tipo_info, list) and len(tipo_info) > 0:
                    actividad = tipo_info[0].get("nombre", "Actividad no definida")
                elif isinstance(tipo_info, dict):
                    actividad = tipo_info.get("nombre", "Actividad no definida")
            else:
                actividad = "Actividad no definida"
            label = f"{fecha_str} - {turno} - {actividad}"
            eventos.append({
                "id": row.get("id"),
                "title": label,
                "start": f"{row['fecha']}T09:00",  # Simplificación; ajustar según turno si se requiere
                "end": f"{row['fecha']}T11:00",
                "backgroundColor": "#33A1FF"
            })
        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            },
            "initialDate": fecha_inicio.isoformat(),
            "initialView": "dayGridMonth" if vista == "Mensual" else "timeGridWeek" if vista == "Semanal" else "timeGridDay",
            "selectable": True,
            "editable": False,
            "eventLimit": True,
            "height": 800
        }
        st.subheader("Calendario de Actividades")
        cal_data = calendar(events=eventos, options=calendar_options, key="cal")
        if cal_data.get("eventClick"):
            event_id = cal_data["eventClick"]["event"]["id"]
            evento = next((e for e in eventos if e["id"] == event_id), None)
            if evento:
                st.info(f"Detalles:\n{evento['title']}")
        st.subheader("Visualización Gráfica")
        fig = generate_activity_calendar(df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay actividades en el rango seleccionado.")

if __name__ == "__main__":
    main()
