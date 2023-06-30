import copy
import pickle
from datetime import datetime, timedelta, date
from math import ceil

from database import utils as db
from database.utils import redisx
from resources.service.categorias import get_all_categories
from resources.service.extras import select_extras_by_id_product


def prices_db():
    prices = redisx.get(f'cotizacion')
    if prices is None:
        sql = "select * from cotizacion;"
        prices = db.select_multiple(sql)
        redisx.set(f'cotizacion', pickle.dumps(prices))
    else:
        prices = pickle.loads(prices)

    data = {}
    for p in prices:
        data[p['key']] = p['value']
    return data


def update_prices(request):
    sql = ""
    for k, v in request.items():
        sql += f"update cotizacion set value='{v}' where key='{k}';"
    db.update_sql(sql)
    redisx.delete('cotizacion')
    try:
        redisx.delete(*redisx.keys('producto:*:precio'))
    except:
        pass
    try:
        redisx.delete(*redisx.keys('producto:*:piezas'))
    except:
        pass


def get_margen(id_producto):
    producto = redisx.get(f'producto:{id_producto}:detalle')
    if producto is None:
        sql = "SELECT cats.margen AS margen FROM productos AS p " \
              f"INNER JOIN categorias as cats ON cats.id = p.idcategoria WHERE p.id= '{id_producto}';"
        return db.select_first(sql)["margen"]
    return [c for c in get_all_categories() if c['id'] == pickle.loads(producto)['idcategoria']][0]['margen']


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


def insert_precio_unitario(id_producto, precio_unitario, rest_days=0):
    fecha = (datetime.now() - timedelta(rest_days)).strftime('%Y-%m-%d')  # 2021-11-18
    precio_unitario = float(precio_unitario)
    sql = f"DELETE FROM precio_unitario WHERE idproducto='{id_producto}'"
    db.delete_sql(sql)
    sql = f"INSERT INTO precio_unitario(idproducto, precioUnitario, fechaActualizacion)" \
          f" VALUES('{id_producto}','{precio_unitario}','{fecha}') RETURNING id;"
    db.insert_sql(sql)
    redisx.delete(f'producto:{id_producto}:precio')
    redisx.delete(f'productos')
    return


def get_precio_unitario(id_producto):
    precio_unitario = redisx.get(f'producto:{id_producto}:precio')
    if precio_unitario is None:
        sql = f"SELECT preciounitario, fechaactualizacion " \
              f"FROM precio_unitario WHERE idproducto='{id_producto}' ORDER BY id DESC;"
        precio_unitario = db.select_first(sql)
        redisx.set(f'producto:{id_producto}:precio', pickle.dumps(precio_unitario))
    else:
        precio_unitario = pickle.loads(precio_unitario)

    costo_material = get_costo_total(id_producto)
    _, extra_total = select_extras_by_id_product(id_producto)
    costo_total = costo_material + extra_total
    precio_unitario["costototal"] = round(costo_total, 2)
    precio_unitario["preciosugerido"] = None

    if not precio_unitario.get('preciounitario', False):
        precio_unitario["preciounitario"] = 0
        precio_unitario["ganancia"] = 0

    precio_u = precio_unitario.get("preciounitario", 0)
    ganancia = max(0, precio_u - costo_total)
    precio_unitario["ganancia"] = round(ganancia, 2)
    # precio_sugerido = costo_total / (1 - get_margen(id_producto) / 100)
    precio_sugerido = (costo_material / (1 - get_margen(id_producto) / 100)) + extra_total
    precio_sugerido = 50 * ceil(precio_sugerido / 50)
    if precio_u != precio_sugerido:
        # Si el precio unitario es distinto al precio sugerido por el sistema, se recomienda nuevo precio según margen
        precio_unitario["preciosugerido"] = round(precio_sugerido, 2)
        check = (date.today() - precio_unitario.get('fechaactualizacion', date.today())).days
        if check < (int(prices_db()["diasVencimiento"]) + 1) and precio_u > precio_sugerido:
            insert_precio_unitario(id_producto,
                                   precio_unitario["preciounitario"],
                                   int(prices_db()["diasVencimiento"]) + 1)
        else:
            insert_precio_unitario(id_producto,
                                   precio_unitario["preciounitario"])

    return precio_unitario


def get_precio_unitario_by_product_id(id_producto):
    precio_unitario = redisx.get(f'producto:{id_producto}:precio')
    if precio_unitario is None:
        sql = f"SELECT preciounitario, fechaactualizacion " \
              f"FROM precio_unitario WHERE idproducto='{id_producto}' ORDER BY id DESC;"
        precio_unitario = db.select_first(sql)
        redisx.set(f'producto:{id_producto}:precio', pickle.dumps(precio_unitario))
    else:
        precio_unitario = pickle.loads(precio_unitario)
    precio_unitario = precio_unitario.get("preciounitario", 0)
    return precio_unitario


def get_costo_total(id_producto):
    piezas = redisx.get(f'producto:{id_producto}:piezas')
    if piezas is None:
        sql = f"select COALESCE(sum(horas),0) as horas,COALESCE(sum(minutos),0) as minutos, COALESCE(sum(peso),0) as peso " \
              f"from piezas where idproducto = {id_producto};"
        total_piezas = db.select_first(sql)
    else:
        piezas = pickle.loads(piezas)
        total_piezas = {}
        total_piezas["horas"] = sum(item['horas'] for item in piezas)
        total_piezas["minutos"] = sum(item['minutos'] for item in piezas)
        total_piezas["peso"] = sum(item['peso'] for item in piezas)

    data = get_price(total_piezas["horas"], total_piezas["minutos"], total_piezas["peso"])
    return round(data['costoPieza'], 2)


def precios_por_mayor(id_producto, unidades_minimas=20, unidades_maximas=100):
    costo_material = get_costo_total(id_producto)
    _, extra_total = select_extras_by_id_product(id_producto)
    precio_u = get_precio_unitario_by_product_id(id_producto)

    # Rango de unidades
    p_maximo = unidades_maximas - unidades_minimas

    precio_minimo = (costo_material / (1 - (get_margen(id_producto) * 0.80) / 100)) + extra_total  # TODO Configurable
    precio_maximo = precio_u - (precio_u - precio_minimo) * 45 / 100  # TODO Configurable
    diferencia = precio_maximo - precio_minimo

    saltos = 5  # TODO Configurable

    precios = []
    for x in range(unidades_minimas, unidades_maximas + saltos, saltos):
        y = x - unidades_minimas
        porcentaje = y * 100 / p_maximo
        p = (precio_minimo + (diferencia * (100 - porcentaje) / 100)) * x
        p = 50 * ceil(p / 50)
        precios.append({"unidades": x,
                        "precio": round(p, 2),
                        "unidad": round(p / x, 2)})
    return {"precios": precios}
