import locale
from datetime import datetime
from database import utils as db
from resources.service import estados as estados
from resources.service.ventas import get_all_ventas


def get_balance():
    sql = f"SELECT date_trunc('month', fechapago) AS mes, COALESCE(sum(monto),0) as ingreso " \
          f"FROM pagos GROUP BY mes order by mes desc;"
    meses = db.select_multiple(sql)

    for m in meses:
        m["mes"] = m["mes"].strftime('%m-%Y')

    ingreso_total = sum([float(m["ingreso"]) for m in meses])
    estado_cancelado = estados.get_id_estado_cancelado()

    # sql = f"SELECT COALESCE(sum(preciounidad),0) as total FROM ventas_productos where idestado <> {estado_cancelado};"
    # precio_unitario_total = float(db.select_first(sql)["total"])
    ventas = get_all_ventas()
    falta_cobrar = sum([float(v["preciototal"] - v["senia"]) for v in ventas])

    sql = f"SELECT COALESCE(sum(monto),0) as total FROM gastos;"
    gastos_total = float(db.select_first(sql)["total"])

    response = {}
    response["ingresoTotal"] = round(ingreso_total, 2)
    response["gastosTotal"] = round(gastos_total, 2)
    response["faltaCobrar"] = round(falta_cobrar, 2)
    response["enCaja"] = round(ingreso_total - gastos_total, 2)
    response["meses"] = meses

    return response
