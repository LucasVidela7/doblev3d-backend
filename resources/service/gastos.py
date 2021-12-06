from datetime import datetime

from database import utils as db


def insertar_gastos(request):
    gastos = request["gastos"]
    fecha_gasto = datetime.now().strftime('%Y-%m-%d')

    for g in gastos:
        monto = float(g["monto"])
        descripcion = g["descripcion"]
        sql = f"INSERT INTO gastos(monto,descripcion, fechaGasto) " \
              f"VALUES('{monto}','{descripcion}','{fecha_gasto}');"
        db.insert_sql(sql)


def get_gastos():
    sql = f"SELECT * from pagos where fechapago >  CURRENT_DATE - INTERVAL '30 days';"
    return db.select_multiple(sql)


def borrar_gasto(id_gasto):
    sql = f"delete from gastos where id='{id_gasto}';"
    return db.delete_sql(sql)
