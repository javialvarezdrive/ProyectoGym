# pages/calendario.py
import streamlit as st
from datetime import datetime, timedelta
from utils.auth import check_login
from utils.database import get_actividades
from utils.helpers import generate_activity_calendar
from streamlit_calendar import calendar

def main():
    check_login()
    st.title("Calendario de Actividades")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mes = st.selectbox("Mes", list(range(1,13)), index=datetime.now().month-1)
    with col2:
        año = st.selectbox("Año", list(range(datetime.now().year-1, datetime.now().year+3)), index=1)
    with col3:
        vista = st.selectbox("Vista", ["Mensual", "Semanal", "Diaria"])
        
    if vista=="Mensual":
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = datetime(año, mes+1, 1)-timedelta(days=1) if mes<12 else datetime(año+1, 1, 1)-timedelta(days=1)
    elif vista=="Semanal":
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = fecha_inicio + timedelta(days=6)
    else:
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = fecha_inicio
        
    filtros = {"fecha_inicio": fecha_inicio.isoformat(), "fecha_fin": fecha_fin.isoformat()}
    df = get_actividades(filtros)
    if not df.empty:
        eventos = []
        for _, row in df.iterrows():
            fecha = row["fecha"]
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            # Acceso seguro a datos anidados
            tipo_nombre = (row.get("tipos_actividad") or {}).get("nombre", "Desconocido")
            usuario = row.get("usuarios") or {}
            usuario_nombre = usuario.get("nombre", "Desconocido")
            
            color = "#FF5733" if tipo_nombre=="Defensa Personal" else "#33A1FF"
            if row.get("turno")=="Mañana":
                inicio_h = "09:00"
                fin_h = "11:00"
            elif row.get("turno")=="Tarde":
                inicio_h = "15:00"
                fin_h = "17:00"
            else:
                inicio_h = "20:00"
                fin_h = "22:00"
            eventos.append({
                "id": row.get("id"),
                "title": f"{tipo_nombre} - {usuario_nombre}",
                "start": f"{fecha.isoformat()}T{inicio_h}",
                "end": f"{fecha.isoformat()}T{fin_h}",
                "backgroundColor": color,
                "description": f"Usuario: {(usuario.get('nip') or 'N/A')} - {usuario_nombre} {usuario.get('apellidos','')}"
            })
        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            },
            "initialDate": fecha_inicio.isoformat(),
            "initialView": "dayGridMonth" if vista=="Mensual" else "timeGridWeek" if vista=="Semanal" else "timeGridDay",
            "selectable": True,
            "editable": False,
            "eventLimit": True,
            "height": 800
        }
        st.subheader("Calendario de Actividades")
        cal_data = calendar(events=eventos, options=calendar_options, key="cal")
        if cal_data.get("eventClick"):
            event_id = cal_data["eventClick"]["event"]["id"]
            evento = next((e for e in eventos if e["id"]==event_id), None)
            if evento:
                st.info(f"Detalles:\n{evento['description']}")
        st.subheader("Visualización gráfica")
        fig = generate_activity_calendar(df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay actividades en este período")
        
if __name__ == "__main__":
    main()
