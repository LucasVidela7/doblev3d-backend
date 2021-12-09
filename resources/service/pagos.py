from datetime import datetime
from database import utils as db


def insertar_pago(request):
    monto = float(request["monto"])
    id_venta = int(request["idVenta"])
    id_medio_pago = int(request["idMedioPago"])
    fecha_pago = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18

    sql = f"INSERT INTO pagos (monto, idventa, fechaPago,idMedioPago) VALUES " \
          f"('{monto}','{id_venta}','{fecha_pago}','{id_medio_pago}') RETURNING id;"
    id_pago = db.insert_sql(sql, key='id')
    return id_pago


def get_all_pagos():
    sql = f"select p.*, mp.descripcion, v.cliente FROM pagos as p " \
          f"INNER JOIN medios_pago AS mp ON mp.id = p.idMedioPago " \
          f"INNER JOIN ventas AS v ON v.id = p.idventa; "
    pagos = db.select_multiple(sql)
    for p in pagos:
        p["fechapago"] = p["fechapago"].strftime('%Y-%m-%d')
    return pagos


def get_all_pagos_by_id_venta(id_venta):
    sql = f"select p.*, mp.descripcion FROM pagos as p " \
          f"INNER JOIN medios_pago AS mp ON mp.id = p.idMedioPago " \
          f"WHERE idventa = '{id_venta}';"
    pagos = db.select_multiple(sql)
    for p in pagos:
        p["fechapago"] = p["fechapago"].strftime('%Y-%m-%d')
    return pagos


def get_all_medios_pago():
    sql = f"select * from medios_pago;"
    return db.select_multiple(sql)


def borrar_pago(id_pago):
    sql = f"delete from pagos where id='{id_pago}';"
    return db.delete_sql(sql)
