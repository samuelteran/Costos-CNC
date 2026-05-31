import streamlit as st
import ezdxf
import math
import tempfile
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle

if 'base_datos_cortes' not in st.session_state:
    st.session_state.base_datos_cortes = {
        "Laser 2mm": 20.0,
        "Laser 6mm": 35.0,
        "Laser 10mm": 70.0,
        "Laser 12mm": 85.0
    }

def procesar_dxf(archivo_path):
    doc = ezdxf.readfile(archivo_path)
    msp = doc.modelspace()
    longitud_total = 0.0
    fig, ax = plt.subplots()
    
    for entity in msp:
        if entity.dxftype() == 'LINE':
            longitud_total += math.dist(entity.dxf.start, entity.dxf.end)
            ax.plot([entity.dxf.start[0], entity.dxf.end[0]], [entity.dxf.start[1], entity.dxf.end[1]], color='blue')
        elif entity.dxftype() == 'CIRCLE':
            longitud_total += 2 * math.pi * entity.dxf.radius
            ax.add_patch(Circle((entity.dxf.center[0], entity.dxf.center[1]), entity.dxf.radius, color='green', fill=False))
        elif entity.dxftype() == 'ARC':
            ang_rad = math.radians(entity.dxf.end_angle - entity.dxf.start_angle)
            longitud_total += entity.dxf.radius * abs(ang_rad)
            ax.add_patch(Arc((entity.dxf.center[0], entity.dxf.center[1]), entity.dxf.radius*2, entity.dxf.radius*2, 
                             theta1=entity.dxf.start_angle, theta2=entity.dxf.end_angle, color='green'))
        elif entity.dxftype() == 'LWPOLYLINE':
            pts = [(v[0], v[1]) for v in entity.vertices()]
            for i in range(len(pts) - 1):
                longitud_total += math.dist(pts[i], pts[i+1])
                ax.plot([pts[i][0], pts[i+1][0]], [pts[i][1], pts[i+1][1]], color='red')
            if entity.closed:
                longitud_total += math.dist(pts[-1], pts[0])
                ax.plot([pts[-1][0], pts[0][0]], [pts[-1][1], pts[0][1]], color='red')
    
    ax.set_aspect('equal')
    return longitud_total / 1000, fig

st.title("⚙️ Cotizador CNC - Sam")

tabs = st.tabs(["Cotizador", "Cortes", "Info"])

with tabs[1]:
    st.header("Gestión de Costos de Corte")
    with st.form("editor_cortes"):
        nombre = st.text_input("Nombre del Método")
        costo_c = st.number_input("Costo por metro lineal (Bs)", value=35.0)
        if st.form_submit_button("Guardar / Actualizar"):
            st.session_state.base_datos_cortes[nombre] = costo_c
            st.rerun()
    for nombre, costo in st.session_state.base_datos_cortes.items():
        st.write(f"**{nombre}**: {costo} Bs/m")

with tabs[0]:
    metodo = st.selectbox("Selecciona Método", list(st.session_state.base_datos_cortes.keys()))
    uploaded_file = st.file_uploader("Sube tu DXF (en mm)", type=["dxf"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        try:
            long_m, fig = procesar_dxf(tmp_path)
            precio_unitario = st.session_state.base_datos_cortes[metodo]
            total = long_m * precio_unitario
            
            st.metric("Longitud Total de Corte", f"{long_m:.2f} m")
            st.subheader(f"Costo Total: {total:.2f} Bs")
            st.pyplot(fig)
        finally:
            os.remove(tmp_path)

with tabs[2]:
    st.header("Manual de Usuario")
    st.write("Bienvenido al Cotizador CNC. Esta herramienta calcula el costo basándose únicamente en la longitud de corte.")
    st.markdown("""
    1. **Formato:** Archivos `.dxf`.
    2. **Preparación:** Asegúrate de que tus líneas estén bien conectadas.
    3. **Cálculo:** El sistema suma el perímetro de todas las formas detectadas.
    4. **Precios:** Puedes ajustar el costo por metro lineal en la pestaña 'CORTES'.
    """)

# Hecho por Samuel Terán Heredia