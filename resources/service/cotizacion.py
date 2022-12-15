import copy
from datetime import datetime

from database import utils as db
from resources.service.extras import select_extras_by_id_product


def prices_db():
    sql = "select * from cotizacion;"
    prices = db.select_multiple(sql)
    data = {}
    for p in prices:
        data[p['key']] = p['value']
    return data


def update_prices(request):
    sql = ""
    for k, v in request.items():
        sql += f"update cotizacion set value='{v}' where key='{k}';"

    db.update_sql(sql)


def get_margen(id_producto):
    sql = "SELECT cats.margen AS margen FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria WHERE p.id= '{id_producto}';"
    return db.select_first(sql)["margen"]


def get_price(hours, minutes, weight):
    price_config = prices_db()
    coste_plastico = price_config["costePlastico"] / 1000
    coste_luz = price_config["costeEnergetico"] * price_config["consumoMedio"]
    coste_amortizacion = price_config["valorImpresora"]
    coste_amortizacion /= (price_config["tiempoDepresiacion"] / 12) * price_config["diasActiva"] * price_config[
        "horasDia"]
    taza_fallos = price_config["tasaFallos"] / 100

    plastico = weight * coste_plastico
    tiempo = hours + (minutes / 60)
    electricidad = tiempo * coste_luz
    amortizacion = coste_amortizacion * tiempo
    taza_fallos = (plastico + tiempo + electricidad + amortizacion) * taza_fallos

    data = {
        "plastico": plastico,
        "electricidad": electricidad,
        "costoAmortizacion": amortizacion,
        "tazaFallos": taza_fallos,
        "costoPieza": plastico + electricidad + amortizacion + taza_fallos
    }

    return data


def get_price_piezas(piezas: list):
    all_prices = {}
    total_horas, total_minutos, total_peso = 0, 0, 0
    for n, p in enumerate(piezas):
        horas = p["horas"]
        minutos = p["minutos"]
        peso = p["peso"]
        data = get_price(horas, minutos, peso)
        p["cotizacion"] = copy.deepcopy(data)
        p["cotizacion"] = {k: round(v, 2) for k, v in p["cotizacion"].items()}

        total_horas += horas
        total_minutos += minutos
        total_peso += peso

        if not n:
            all_prices = copy.deepcopy(data)
            all_prices["costoElaboracion"] = data["costoPieza"]
        else:
            all_prices["plastico"] += data["plastico"]
            all_prices["electricidad"] += data["electricidad"]
            all_prices["costoAmortizacion"] += data["costoAmortizacion"]
            all_prices["tazaFallos"] += data["tazaFallos"]
            all_prices["costoElaboracion"] += data["costoPieza"]

    all_prices = {k: round(v, 2) for k, v in all_prices.items()}
    all_prices["totalHoras"] = total_horas + int(total_minutos / 60)
    all_prices["totalMinutos"] = int(total_minutos % 60)
    all_prices["totalPeso"] = int(total_peso)

    return piezas, all_prices


def insert_precio_unitario(id_producto, request):
    fecha = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18
    precio_unitario = float(request["preciounitario"])
    costo_total = float(request["costoTotal"])
    ganancia = round(precio_unitario - costo_total, 2)

    sql = f"INSERT INTO precio_unitario(idproducto, precioUnitario, ganancia, costoTotal, fechaActualizacion)" \
          f" VALUES('{id_producto}','{precio_unitario}','{ganancia}','{costo_total}','{fecha}') RETURNING id;"
    id = db.insert_sql(sql, key="id")
    if id:
        sql = f"DELETE FROM precio_unitario WHERE idproducto='{id_producto}' and id<>'{id}';"
        db.delete_sql(sql)
    return


def get_precio_unitario(id_producto):
    sql = f"SELECT preciounitario, ganancia, costototal, fechaactualizacion " \
          f"FROM precio_unitario WHERE idproducto='{id_producto}' ORDER BY id DESC;"
    precio_unitario = db.select_first(sql)

    costo_material = get_costo_total(id_producto)
    _, extra_total = select_extras_by_id_product(id_producto)
    costo_total = costo_material + extra_total
    precio_unitario["costototal"] = costo_total
    precio_unitario["preciosugerido"] = None

    if not precio_unitario:
        precio_unitario["preciounitario"] = 0
        precio_unitario["ganancia"] = 0

    precio_u = precio_unitario.get("preciounitario", 0)
    ganancia = precio_u - costo_total
    precio_unitario["ganancia"] = round(ganancia, 2)
    precio_sugerido = costo_total / (1 - get_margen(id_producto) / 100)
    if precio_u < precio_sugerido:
        # Si el precio unitario es menor al precio sugerido por el sistema, se recomienda nuevo precio
        precio_unitario["preciosugerido"] = round(precio_sugerido, 2)

    return precio_unitario


def get_precio_unitario_by_product_id(id_producto):
    sql = f"SELECT * FROM precio_unitario WHERE idproducto='{id_producto}' ORDER BY id DESC;"
    precio_unitario = db.select_first(sql).get("preciounitario", 0)
    return precio_unitario


def get_precio_unitario_vencido(id_producto):
    return True


def get_costo_total(id_producto):
    sql = f"select COALESCE(sum(horas),0) as horas,COALESCE(sum(minutos),0) as minutos, COALESCE(sum(peso),0) as peso " \
          f"from piezas where idproducto = {id_producto};"
    total_piezas = db.select_first(sql)
    data = get_price(total_piezas["horas"], total_piezas["minutos"], total_piezas["peso"])
    return round(data['costoPieza'], 2)
