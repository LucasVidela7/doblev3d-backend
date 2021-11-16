import copy

from database import utils as db


def prices_db():
    sql = "select * from cotizacion;"
    prices = db.select_multiple(sql)
    data = {}
    for p in prices:
        data[p['key']] = p['value']
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
1