from datetime import datetime

from database import utils as db


def insertar_gastos(request):
    fecha_gasto = datetime.now().strftime('%Y-%m-%d')

    for g in request:
        monto = float(g["monto"])
        descripcion = g["descripcion"]
        tipo = g["tipo"]
        sql = f"INSERT INTO gastos(monto,descripcion, fechaGasto, tipo) " \
              f"VALUES('{monto}','{descripcion}','{fecha_gasto}', '{tipo}');"
        db.insert_sql(sql)


def get_gastos():
    sql = f"SELECT * from gastos where fechaGasto >  CURRENT_DATE - INTERVAL '30 days';"
    return db.select_multiple(sql)


def borrar_gasto(id_gasto):
    sql = f"delete from gastos where id='{id_gasto}';"
    return db.delete_sql(sql)
