from datetime import datetime
from sqlite3 import Error

import psycopg2
import psycopg2.extras

# from database.connection import create_connection
from resources.service import categorias as categorias

from database import utils as db


def insert_product(request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 11/11/2021

    sql = f"""INSERT INTO productos(descripcion,idCategoria, fechaCreacion)
            VALUES('{descripcion}','{id_categoria}','{fecha_creacion}') RETURNING id;"""
    id_product = db.insert_sql(sql, key='id')
    if id_product:
        for pieza in request.get("piezas", []):
            desc_piezas = pieza["descripcion"]
            peso_piezas = int(pieza["peso"])
            horas_piezas = int(pieza["horas"])
            minutos_piezas = int(pieza["minutos"])
            sql = f"""INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto)
                    VALUES('{desc_piezas}','{peso_piezas}','{horas_piezas}','{minutos_piezas}','{id_product}');
            """
            db.insert_sql(sql)
        for id_extra in request.get("extras", []):
            sql = f"""INSERT INTO extra_producto(idproducto, idextra)
                    VALUES('{id_product}','{id_extra}');"""
            db.insert_sql(sql)
        return id_product


def select_product_by_id(_id):
    sql = f"SELECT * FROM productos WHERE id= {_id}"
    product = db.select_first(sql)
    product["fechacreacion"] = product["fechacreacion"].strftime('%Y-%m-%d')
    return product


def get_all_products():
    sql = f"SELECT * FROM productos ORDER BY estado DESC, id DESC"
    products = [dict(p) for p in db.select_multiple(sql)]
    list_cat = categorias.get_all_categories()
    list_cat = dict(map(lambda x: (x["id"], x), list_cat))
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
        try:
            print(list_cat[p["idcategoria"]])
            p["idcategoria"] = list_cat[p["idcategoria"]]["categoria"]
        except:
            continue
    return products


def update_product(id_product, request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    estado = request['estado']

    sql = f"UPDATE productos SET descripcion='{descripcion}', idCategoria='{id_categoria}', estado='{estado}' where id={id_product}"
    db.update_sql(sql)
    sql = f"DELETE FROM piezas where idProducto={id_product}"
    db.delete_sql(sql)

    for pieza in request.get("piezas", []):
        desc_piezas = pieza["descripcion"]
        peso_piezas = int(pieza["peso"])
        horas_piezas = int(pieza["horas"])
        minutos_piezas = int(pieza["minutos"])
        sql = f"""INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto)
                VALUES('{desc_piezas}','{peso_piezas}','{horas_piezas}','{minutos_piezas}','{id_product}');"""
        db.insert_sql(sql)
    sql = f"DELETE FROM extra_producto where idProducto={id_product}"
    db.delete_sql(sql)

    for id_extra in request.get("extras", []):
        sql = f"""INSERT INTO extra_producto(idproducto, idextra)
                VALUES('{id_product}','{id_extra}');"""
        db.insert_sql(sql)
    return id_product