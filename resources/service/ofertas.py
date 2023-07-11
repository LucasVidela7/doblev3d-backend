import json

from database import utils as db
from resources.service.ventas import get_all_ventas


def get_ofertas():
    sql = """SELECT *,
     TO_CHAR(fecha_desde,'YYYY-MM-DD') as fecha_desde,
     TO_CHAR(fecha_hasta,'YYYY-MM-DD') as fecha_hasta
     FROM ofertas"""
    response = db.select_multiple(sql)
    return response


def get_ofertas_vigentes():
    sql = """SELECT *,
     TO_CHAR(fecha_desde,'YYYY-MM-DD') as fecha_desde,
     TO_CHAR(fecha_hasta,'YYYY-MM-DD') as fecha_hasta
     FROM ofertas
     WHERE fecha_desde <= now() and fecha_hasta >= now();"""
    response = db.select_multiple(sql)
    return response


def get_tipo_ofertas():
    sql = """SELECT tipo as id, tipo as descripcion FROM public.ofertas_tipo
    ORDER BY id ASC """
    return db.select_multiple(sql)


def crear_oferta_tienda(fecha_desde, fecha_hasta, porcentaje, label, login=False):
    sql = f"""INSERT INTO ofertas (tipo,fecha_desde, fecha_hasta, login, porcentaje, label) 
    VALUES ('TIENDA','{fecha_desde}', '{fecha_hasta}', '{login}', '{porcentaje}', '{label}')"""
    db.insert_sql(sql)
    return True


def crear_oferta_categoria(fecha_desde, fecha_hasta, porcentaje, id_categoria, label, login=False):
    objeto = json.dumps({'id_categoria': id_categoria})

    sql = f"""INSERT INTO ofertas (tipo,fecha_desde, fecha_hasta, login, porcentaje, label, objeto) 
    VALUES ('CATEGORIA','{fecha_desde}', '{fecha_hasta}', '{login}', '{porcentaje}', '{label}', '{objeto}')"""
    db.insert_sql(sql)
    return True
