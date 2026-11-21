from datetime import datetime
from subrutinas import (
    obtener_bd,
    consulta_filtrada_ordenada,
    consulta_rango_fechas,
    consulta_agregacion_lookup,
    filtrar_duracion_mayor_200
)

if __name__ == "__main__":
    db = obtener_bd()

    # 1. Filtro, proyección y ordenamiento múltiple
    consulta_filtrada_ordenada(db, provincia="Puntarenas", limite=10)

    # 2. Rango de fechas con formato en español
    inicio = datetime(2025, 2, 1, 0, 0, 0)
    fin = datetime(2025, 10, 31, 23, 59, 59)
    lote_fechas = consulta_rango_fechas(db, inicio, fin, limite=50)

    # 3. Agregación con $lookup
    consulta_agregacion_lookup(db, limite=10)

    # 4. List comprehension sobre resultados obtenidos
    filtrar_duracion_mayor_200(lote_fechas)