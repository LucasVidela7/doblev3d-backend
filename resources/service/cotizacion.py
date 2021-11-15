import copy

from database.connection import create_connection


def prices_db():
    conn = create_connection()
    cur = conn.cursor()
    sql = "select * from cotizacion;"
    cur.execute(sql)
    prices = cur.fetchall()
    data = {}
    for p in prices:
        data[p[0]] = p[1]
    return data


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
    for n, p in enumerate(piezas):
        pl, el, am, tf = get_price(p["horas"], p["minutos"], p["peso"])
        data = {
            "costeMaterial": {
                "plastico": pl,
                "electricidad": el
            },
            "costoAmortizaion": am,
            "tazaFallos": tf
        }
        p["cotizacion"] = copy.deepcopy(data)

        if not n:
            all_prices = copy.deepcopy(data)
        else:
            all_prices["costeMaterial"]["plastico"] += pl
            all_prices["costeMaterial"]["electricidad"] += el
            all_prices["costoAmortizaion"] += am
            all_prices["tazaFallos"] += tf

    return piezas, all_prices
