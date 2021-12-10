from datetime import datetime

from database import utils as db


def insertar_gastos(request):
    fecha_gasto = datetime.now().strftime('%Y-%m-%d')

    list_total_gastos = []
    for g in request:
        monto = float(g["monto"])
        descripcion = g["descripcion"]
        tipo = g["tipo"]
        list_gastos = [monto, descripcion, fecha_gasto, tipo]
        list_total_gastos.append(list_gastos)

    values = ""
    for l in list_total_gastos:
        values += '(' + ",".join(f"'{c}'" for c in l) + '),'
    values = values[:-1]
    sql = f"INSERT INTO gastos(monto,descripcion, fechaGasto, tipo) " \
          f"VALUES{values};"
    db.insert_sql(sql)


def get_gastos():
    sql = f"SELECT * from gastos where fechaGasto >  CURRENT_DATE - INTERVAL '30 days';"
    return db.select_multiple(sql)


def borrar_gasto(id_gasto):
    sql = f"delete from gastos where id='{id_gasto}';"
    return db.delete_sql(sql)
