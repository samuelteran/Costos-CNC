import ezdxf
import math

def calcular_cotizacion(archivo_dxf, espesor, costo_m2_material, costo_metro_lineal_corte, area_plancha_usada):
    doc = ezdxf.readfile(archivo_dxf)
    msp = doc.modelspace()
    
    longitud_total = 0.0
    
    # Iterar sobre entidades geométricas comunes de corte
    for entity in msp:
        if entity.dxftype() == 'LINE':
            p1 = entity.dxf.start
            p2 = entity.dxf.end
            longitud_total += math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
            
        elif entity.dxftype() == 'CIRCLE':
            longitud_total += 2 * math.pi * entity.dxf.radius
            
        elif entity.dxftype() == 'ARC':
            longitud_total += entity.dxf.radius * entity.dxf.angle
            
    # Cálculos
    # Conversión de unidades: asumiendo que el dibujo está en milímetros
    longitud_metros = longitud_total / 1000
    
    costo_material = area_plancha_usada * costo_m2_material
    costo_corte = longitud_metros * costo_metro_lineal_corte
    total = costo_material + costo_corte
    
    return costo_material, costo_corte, total

# --- CONFIGURACIÓN DE USUARIO ---
archivo = "tu_plano.dxf" # Asegúrate de convertir tu DWG a DXF
espesor_actual = 6
costo_material_m2 = 150 # Bs por m2 (Ejemplo)
costo_corte_lineal = 35 # Bs por metro (para 6mm)
area_utilizada = 0.5    # m2 de material consumido en el trabajo

c_mat, c_corte, total = calcular_cotizacion(archivo, espesor_actual, costo_material_m2, costo_corte_lineal, area_utilizada)

print(f"--- COTIZACIÓN ---")
print(f"Costo del material: {c_mat:.2f} Bs")
print(f"Costo del corte CNC: {c_corte:.2f} Bs")
print(f"Costo total: {total:.2f} Bs")