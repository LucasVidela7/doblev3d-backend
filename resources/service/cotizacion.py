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


def get_price(hours, minutes, weight):
    price_config = prices_db()
    coste_plastico = price_config["costePlastico"] / 1000
    coste_luz = price_config["costeEnergetico"] * price_config["consumoMedio"]
    coste_amortizacion = price_config["valorImpresora"] / ((price_config["tiempoDepresiacion"] / 12) * price_config[
        "diasActiva"] * price_config["horasDia"])
    taza_fallos = price_config["tasaFallos"] / 100

    plastico = round(weight * coste_plastico, 2)
    tiempo = round(hours + (minutes / 60), 2)
    electricidad = round(tiempo * coste_luz, 2)
    amortizacion = round(coste_amortizacion * tiempo, 2)
    taza_fallos = round((plastico + tiempo + electricidad + amortizacion) * taza_fallos, 2)

    return plastico, electricidad, amortizacion, taza_fallos


def get_price_piezas(piezas: list):
    all_prices = {}
    total_horas, total_minutos, total_peso = 0, 0, 0
    for n, p in enumerate(piezas):
        horas = p["horas"]
        minutos = p["minutos"]
        peso = p["peso"]
        pl, el, am, tf = get_price(horas, minutos, peso)
        data = {
            "plastico": pl,
            "electricidad": el,
            "costoAmortizacion": am,
            "tazaFallos": tf,
            "costoPieza": round(pl + el + am + tf, 2)
        }
        p["cotizacion"] = copy.deepcopy(data)

        total_horas += horas
        total_minutos += minutos
        total_peso += peso

        if not n:
            all_prices = copy.deepcopy(data)
            all_prices["costoElaboracion"] = pl + el + am + tf
        else:
            all_prices["plastico"] += pl
            all_prices["electricidad"] += el
            all_prices["costoAmortizacion"] += am
            all_prices["tazaFallos"] += tf
            all_prices["costoElaboracion"] += pl + el + am + tf

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

    if not precio_unitario:
        precio_unitario["preciosugerido"] = None
        precio_unitario["preciounitario"] = 0
        precio_unitario["ganancia"] = 0
        # return precio_unitario
    # else:
    #     precio_unitario["fechaactualizacion"] = precio_unitario["fechaactualizacion"].strftime('%Y-%m-%d')

    precio_unitario["preciosugerido"] = None
    precio_u = precio_unitario.get("preciounitario", 0)
    ganancia = precio_u - costo_total
    precio_unitario["ganancia"] = round(ganancia, 2)
    ganancia_esperada = costo_material * 1.21
    if ganancia < ganancia_esperada:
        diferencia = ganancia_esperada - ganancia
        precio_unitario["preciosugerido"] = round(precio_u + diferencia, 2)

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
    p, e, a, tf = get_price(total_piezas["horas"], total_piezas["minutos"], total_piezas["peso"])
    return round(p + e + a + tf, 2)
