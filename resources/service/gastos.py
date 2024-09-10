from datetime import datetime

from database import utils as db


def insertar_gastos(request):
    fecha_gasto = datetime.now().strftime('%Y-%m-%d')
    monto = float(request["monto"])
    descripcion = request["descripcion"]
    tipo = request["tipo"]
    sql = f"INSERT INTO gastos(monto,descripcion, fechaGasto, tipo) " \
          f"VALUES('{monto}','{descripcion}','{fecha_gasto}','{tipo}') RETURNING id;"
    return db.insert_sql(sql, key='id')


def get_gastos(mes=None, anio=None):
    if mes is None or anio is None:
        mes = datetime.now().month
        anio = datetime.now().year

    sql = f"SELECT * from gastos " \
          f"WHERE EXTRACT(month FROM fechagasto) = {mes} AND EXTRACT(year FROM fechagasto) = {anio} " \
          f"ORDER BY id ASC;"
    gastos = db.select_multiple(sql)
    for g in gastos:
        g["fechagasto"] = g["fechagasto"].strftime('%Y-%m-%d')
    return gastos


def borrar_gasto(id_gasto):
    sql = f"delete from gastos where id='{id_gasto}';"
    return db.delete_sql(sql)
