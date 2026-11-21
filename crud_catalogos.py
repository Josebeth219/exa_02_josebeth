from subrutinas import (
    obtener_bd,
    insertar_categoria,
    modificar_categoria,
    borrar_categoria,
    insertar_observador,
    modificar_observador,
    borrar_observador
)

if __name__ == "__main__":
    db = obtener_bd()

    # Prueba CRUD Categorías
    insertar_categoria(db, {"_id": 99, "nombre": "Nube lenticular anómala", "descripcion": "Prueba temporal"})
    modificar_categoria(db, 99, {"descripcion": "Descripción actualizada correctamente"})
    borrar_categoria(db, 99)

    # Prueba CRUD Observadores
    insertar_observador(db, {"_id": 999, "alias": "Estación Temporal", "rol": "Testigo ciudadano", "indice_confiabilidad": 0.50})
    modificar_observador(db, 999, {"indice_confiabilidad": 0.85})
    borrar_observador(db, 999)