import csv
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# Conjuntos definidos en el examen
CANTONES_COSTEROS = {
    "Puntarenas", "Esparza", "Montes de Oro", "Osa", "Quepos",
    "Golfito", "Parrita", "Corredores", "Garabito", "Liberia", "Nicoya", "Santa Cruz", "Bagaces",
    "Carrillo", "Cañas", "Abangares", "Nandayure", "La Cruz", "Hojancha", "Limón", "Pococí",
    "Siquirres", "Talamanca", "Matina", "Guácimo"
}

CANTONES_MONTANOSOS = {
    "Tarrazú", "Aserrí", "Mora", "Acosta", "Turrubares", "Dota",
    "Pérez Zeledón", "León Cortés", "Puriscal", "San Ramón", "Zarcero", "Poás", "Valverde Vega",
    "Paraíso", "Jiménez", "Turrialba", "Alvarado", "Oreamuno", "El Guarco", "Barva", "Santa Bárbara",
    "San Rafael", "San Isidro", "Tilarán", "Buenos Aires", "Coto Brus"
}

POBLADOS_INSULARES = {
    "Isla del Coco", "Isla Chira", "Isla Venado", "Isla Caballo", "Isla San Lucas",
    "Isla Tortuga", "Isla Cedros", "Isla Jesucita", "Isla Berrugate"
}

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


def obtener_bd():
    cliente = MongoClient("mongodb://localhost:27017/")
    return cliente["rcofa_db"]


def clasificar_tipo_zona(provincia: str, canton: str, poblado: str) -> str:
    if poblado in POBLADOS_INSULARES:
        return "Insular"
    if canton in CANTONES_COSTEROS:
        return "Costera"
    if canton in CANTONES_MONTANOSOS:
        return "Montañosa"
    return "Urbana"


def formatear_fecha_es(fecha_dt: datetime) -> str:
    nombre_mes = MESES_ES.get(fecha_dt.month, "")
    return f"{fecha_dt.day:02d} de {nombre_mes} de {fecha_dt.year} ({fecha_dt.strftime('%H:%M:%S')})"


# ==========================================
# RUBRO 1: CARGA DE DATOS
# ==========================================

def cargar_ubicaciones_csv(db, ruta_csv="ubicaciones.csv"):
    db.ubicaciones.delete_many({})
    documentos = []

    with open(ruta_csv, mode="r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo, delimiter=";")
        for fila in lector:
            provincia = fila["Provincia"].strip()
            canton = fila["Cantón"].strip()
            distrito = fila["Distrito"].strip()
            poblado = fila["Poblado"].strip() if fila["Poblado"] else "Sin especificar"

            tipo_zona = clasificar_tipo_zona(provincia, canton, poblado)

            doc = {
                "id_sector": str(fila["Id"]).strip(),
                "provincia": provincia,
                "canton": canton,
                "distrito": distrito,
                "localidad": poblado,
                "tipo_zona": tipo_zona
            }
            documentos.append(doc)

    if documentos:
        db.ubicaciones.insert_many(documentos)
    print(f"[OK] Se cargaron {len(documentos)} ubicaciones con su 'tipo_zona'.")


def poblar_catalogos_iniciales(db):
    db.categorias_fenomeno.delete_many({})
    db.observadores.delete_many({})

    categorias = [
        {"_id": 1, "nombre": "Luminaria estacionaria", "descripcion": "Luz fija de alta intensidad sin desplazamiento aparente."},
        {"_id": 2, "nombre": "Eco radar no identificado", "descripcion": "Traza detectada en frecuencia de radar sin transpondedor."},
        {"_id": 3, "nombre": "Estela luminosa", "descripcion": "Desplazamiento rápido con rastro ionizado en atmósfera."},
        {"_id": 4, "nombre": "Objeto Volador NO Identificado", "descripcion": "Anomalía aérea con maniobras no convencionales."},
        {"_id": 5, "nombre": "Alteración magnética y acústica", "descripcion": "Variación súbita de brújula acompañada de zumbido de baja frecuencia."}
    ]

    # El rubro exige usar insert_one para categorias_fenomeno
    for cat in categorias:
        db.categorias_fenomeno.insert_one(cat)
    print(f"[OK] Se insertaron {len(categorias)} categorías usando insert_one().")

    observadores = [
        {"_id": 101, "alias": "Estación Volcán Poás", "rol": "Estación meteorológica", "indice_confiabilidad": 0.96},
        {"_id": 102, "alias": "Radar Cerro Chirripó", "rol": "Operador radar", "indice_confiabilidad": 0.98},
        {"_id": 103, "alias": "Vigia_Pacifico_01", "rol": "Testigo ciudadano", "indice_confiabilidad": 0.72},
        {"_id": 104, "alias": "Boya Isla del Coco", "rol": "Estación meteorológica", "indice_confiabilidad": 0.94},
        {"_id": 105, "alias": "Radio_Limon_Sur", "rol": "Operador radar", "indice_confiabilidad": 0.89},
        {"_id": 106, "alias": "Observador_Arenal", "rol": "Testigo ciudadano", "indice_confiabilidad": 0.65}
    ]

    # El rubro exige usar insert_many para observadores
    db.observadores.insert_many(observadores)
    print(f"[OK] Se insertaron {len(observadores)} observadores usando insert_many().")


# ==========================================
# RUBRO 2: MÉTODOS CRUD CATÁLOGOS
# ==========================================

def insertar_categoria(db, categoria: dict):
    db.categorias_fenomeno.insert_one(categoria)
    print(f"Categoría '{categoria.get('nombre')}' insertada.")


def modificar_categoria(db, id_categoria: int, nuevos_datos: dict):
    res = db.categorias_fenomeno.update_one({"_id": id_categoria}, {"$set": nuevos_datos})
    print(f"Categoría {id_categoria} modificada (coincidencias: {res.modified_count}).")


def borrar_categoria(db, id_categoria: int):
    res = db.categorias_fenomeno.delete_one({"_id": id_categoria})
    print(f"Categoría {id_categoria} eliminada (borrados: {res.deleted_count}).")


def insertar_observador(db, observador: dict):
    db.observadores.insert_one(observador)
    print(f"Observador '{observador.get('alias')}' insertado.")


def modificar_observador(db, id_observador: int, nuevos_datos: dict):
    res = db.observadores.update_one({"_id": id_observador}, {"$set": nuevos_datos})
    print(f"Observador {id_observador} modificado (coincidencias: {res.modified_count}).")


def borrar_observador(db, id_observador: int):
    res = db.observadores.delete_one({"_id": id_observador})
    print(f"Observador {id_observador} eliminado (borrados: {res.deleted_count}).")


# ==========================================
# RUBRO 3: DATOS SINTÉTICOS (10,000 REGISTROS)
# ==========================================

def generar_avistamientos_sinteticos(db, cantidad=10000):
    db.avistamientos.delete_many({})

    ids_categorias = [c["_id"] for c in db.categorias_fenomeno.find({}, {"_id": 1})]
    ids_observadores = [o["_id"] for o in db.observadores.find({}, {"_id": 1})]
    ubicaciones = list(db.ubicaciones.find({}, {"_id": 0}))

    if not ids_categorias or not ids_observadores or not ubicaciones:
        print("[ERROR] Debes cargar ubicaciones y catálogos antes de generar avistamientos.")
        return

    fecha_base = datetime(2025, 1, 1, 0, 0, 0)
    registros = []

    for i in range(1, cantidad + 1):
        codigo = f"REP-{str(i).zfill(8)}"

        # Fecha generada como texto y convertida con strptime como pide el enunciado
        segundos_random = random.randint(0, 365 * 24 * 3600)
        fecha_texto = (fecha_base + timedelta(seconds=segundos_random)).strftime("%Y-%m-%d %H:%M:%S")
        fecha_dt = datetime.strptime(fecha_texto, "%Y-%m-%d %H:%M:%S")

        ub = random.choice(ubicaciones)

        doc = {
            "_id": codigo,
            "codigo_reporte": codigo,
            "fecha_evento": fecha_dt,
            "duracion_seg": random.randint(5, 600),
            "id_categoria": random.choice(ids_categorias),
            "id_observador": random.choice(ids_observadores),
            "ubicacion": {
                "id_sector": ub["id_sector"],
                "provincia": ub["provincia"],
                "canton": ub["canton"],
                "distrito": ub["distrito"],
                "localidad": ub["localidad"]
            }
        }

        # Variabilidad no uniforme (esquema flexible en MongoDB)
        perfil = random.random()
        if perfil < 0.45:
            doc["telemetria_entorno"] = {
                "visibilidad_km": round(random.uniform(1.0, 25.0), 1),
                "nubosidad_pct": random.randint(0, 100),
                "viento_nudos": round(random.uniform(0.0, 40.0), 1)
            }
        elif perfil < 0.80:
            doc["anomalia_magnetica"] = {
                "intensidad_gauss": round(random.uniform(0.2, 4.8), 2),
                "frecuencia_hz": random.randint(10, 5000)
            }
            doc["verificado_instrumental"] = True
        else:
            doc["reporte_visual"] = {
                "color_predominante": random.choice(["Blanco", "Ámbar", "Verde esmeralda", "Azul eléctrico"]),
                "trayectoria": random.choice(["Estacionaria", "Zig-zag", "Ascenso vertical", "Horizontal"])
            }

        registros.append(doc)

    db.avistamientos.insert_many(registros)
    print(f"[OK] Se generaron e insertaron {len(registros)} avistamientos sintéticos.")


# ==========================================
# RUBRO 4: CONSULTAS Y AGREGACIONES
# ==========================================

def consulta_filtrada_ordenada(db, provincia="Puntarenas", limite=10):
    print(f"\n--- 1. Avistamientos en {provincia} (Ordenados por duración DESC y fecha ASC) ---")
    filtro = {"ubicacion.provincia": {"$eq": provincia}}
    proyeccion = {
        "_id": 0,
        "codigo_reporte": 1,
        "fecha_evento": 1,
        "duracion_seg": 1,
        "ubicacion.localidad": 1
    }
    cursor = (
        db.avistamientos.find(filtro, proyeccion)
        .sort([("duracion_seg", -1), ("fecha_evento", 1)])
        .limit(limite)
    )
    resultados = list(cursor)
    for r in resultados:
        print(f"{r['codigo_reporte']} | {r['ubicacion']['localidad']} | {r['duracion_seg']}s | {formatear_fecha_es(r['fecha_evento'])}")
    return resultados


def consulta_rango_fechas(db, fecha_inicio: datetime, fecha_fin: datetime, limite=10):
    print(f"\n--- 2. Reportes entre {formatear_fecha_es(fecha_inicio)} y {formatear_fecha_es(fecha_fin)} ---")
    filtro = {"fecha_evento": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    resultados = list(db.avistamientos.find(filtro).limit(limite))
    for r in resultados:
        print(f"{r['codigo_reporte']} | Fecha: {formatear_fecha_es(r['fecha_evento'])} | Duración: {r['duracion_seg']}s")
    return resultados


def consulta_agregacion_lookup(db, limite=10):
    print("\n--- 3. Reporte Consolidado con $lookup ---")
    pipeline = [
        {"$limit": limite},
        {
            "$lookup": {
                "from": "categorias_fenomeno",
                "localField": "id_categoria",
                "foreignField": "_id",
                "as": "categoria_info"
            }
        },
        {
            "$lookup": {
                "from": "observadores",
                "localField": "id_observador",
                "foreignField": "_id",
                "as": "observador_info"
            }
        },
        {"$unwind": "$categoria_info"},
        {"$unwind": "$observador_info"}
    ]
    resultados = list(db.avistamientos.aggregate(pipeline))
    for r in resultados:
        print(
            f"Código: {r['codigo_reporte']} | Fenómeno: {r['categoria_info']['nombre']} | "
            f"Observador: {r['observador_info']['alias']} | Localidad: {r['ubicacion']['localidad']}"
        )
    return resultados


def filtrar_duracion_mayor_200(lista_reportes: list):
    print("\n--- 4. Filtro idiomático en Python (duracion_seg > 200) ---")
    filtrados = [rep for rep in lista_reportes if rep.get("duracion_seg", 0) > 200]
    print(f"De {len(lista_reportes)} reportes analizados, {len(filtrados)} superan los 200 segundos:")
    for r in filtrados[:10]:
        print(f" -> {r['codigo_reporte']} ({r['duracion_seg']}s)")
    return filtrados