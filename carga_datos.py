from subrutinas import (
    obtener_bd,
    cargar_ubicaciones_csv,
    poblar_catalogos_iniciales,
    generar_avistamientos_sinteticos
)

if __name__ == "__main__":
    db = obtener_bd()
    cargar_ubicaciones_csv(db, "ubicaciones.csv")
    poblar_catalogos_iniciales(db)
    generar_avistamientos_sinteticos(db, 10000)