import locale
from datetime import datetime
from database import utils as db
from resources.service import estados as estados
from resources.service.ventas import get_all_ventas


def get_balance():
    # Ingresos
    sql = f"SELECT date_trunc('month', fechapago) AS mes, COALESCE(sum(monto),0) as monto " \
          f"FROM pagos GROUP BY mes order by mes desc;"
    meses_ingresos = db.select_multiple(sql)

    for m in meses_ingresos:
        m["mes"] = m["mes"].strftime('%m-%Y')

    ingreso_total = sum([float(m["monto"]) for m in meses_ingresos])

    # Otros
    ventas = get_all_ventas()
    falta_cobrar = sum([float(v["preciototal"] - v["senia"]) for v in ventas])

    # Gastos
    sql = f"SELECT date_trunc('month', fechagasto) AS mes, COALESCE(sum(monto),0) as monto " \
          f"FROM gastos GROUP BY mes order by mes desc;"
    meses_gastos = db.select_multiple(sql)
    for m in meses_gastos:
        m["mes"] = m["mes"].strftime('%m-%Y')
    gastos_total = sum([float(m["monto"]) for m in meses_gastos])

    response = {}
    response["ingresoTotal"] = round(ingreso_total, 2)
    response["gastosTotal"] = round(gastos_total, 2)
    response["faltaCobrar"] = round(falta_cobrar, 2)
    response["enCaja"] = round(ingreso_total - gastos_total, 2)
    response["meses"] = {"ingresos": meses_ingresos}
    response["meses"].update({"gastos": meses_gastos})

    return response
