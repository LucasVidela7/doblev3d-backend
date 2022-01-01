from database import utils as db
from resources.service.ventas import get_all_ventas


def get_balance():
    # Ingresos
    sql = f"""SELECT date_trunc('month', fecha) AS mes, sum(ingresos) ingresos, sum(gastos) gastos
                FROM (
                SELECT fecha, ingresos, gastos
                FROM
                 (SELECT date_trunc('month', fechapago) AS fecha, sum(monto) as ingresos, 0 gastos from pagos group by fecha) as p
                UNION
                (SELECT date_trunc('month', fechagasto) AS fecha, 0 ingresos, sum(monto) as gastos from gastos group by fecha)
                ) as t
            group by mes
            order by mes desc;
    """
    meses = db.select_multiple(sql)

    ingreso_total = 0
    gastos_total = 0

    for m in meses:
        m["mes"] = m["mes"].strftime('%m-%Y')
        ingreso_total += m["ingresos"]
        gastos_total += m["gastos"]

    # Otros
    ventas = get_all_ventas()
    falta_cobrar = sum([float(v["preciototal"] - v["senia"]) for v in ventas])

    response = {}
    response["ingresoTotal"] = round(ingreso_total, 2)
    response["gastosTotal"] = round(gastos_total, 2)
    response["faltaCobrar"] = round(falta_cobrar, 2)
    response["enCaja"] = round(ingreso_total - gastos_total, 2)
    response["meses"] = meses[:12]

    return response
