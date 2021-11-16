from datetime import datetime
from sqlite3 import Error

import psycopg2
import psycopg2.extras

from database.connection import create_connection
from resources.service import categorias as categorias


def insert_product(request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 11/11/2021

    conn = create_connection()
    sql = f"""INSERT INTO productos(descripcion,idCategoria, fechaCreacion)
            VALUES('{descripcion}','{id_categoria}','{fecha_creacion}') RETURNING id;"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        id_product = cur.fetchone()[0]
        if id_product:
            for pieza in request.get("piezas", []):
                desc_piezas = pieza["descripcion"]
                peso_piezas = int(pieza["peso"])
                horas_piezas = int(pieza["horas"])
                minutos_piezas = int(pieza["minutos"])
                sql = f"""INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto)
                        VALUES('{desc_piezas}','{peso_piezas}','{horas_piezas}','{minutos_piezas}','{id_product}');
                """
                cur.execute(sql)
                conn.commit()
            for id_extra in request.get("extras", []):
                sql = f"""INSERT INTO extra_producto(idproducto, idextra)
                        VALUES('{id_product}','{id_extra}');"""
                cur.execute(sql)
                conn.commit()
            return id_product
    except Error as e:
        print(str(e))
        return False
    finally:
        if conn:
            conn.close()


def select_product_by_id(_id):
    conn = create_connection()
    sql = f"SELECT * FROM productos WHERE id= {_id}"

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        product = dict(cur.fetchone())
        product["fechacreacion"] = product["fechacreacion"].strftime('%Y-%m-%d')
        return product
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()


def get_all_products():
    conn = create_connection()
    sql = f"SELECT * FROM productos ORDER BY id DESC"

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        products = [dict(p) for p in cur.fetchall()]
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
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()


def update_product(id_product, request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    estado = request['estado']

    conn = create_connection()
    sql = f"UPDATE productos SET descripcion='{descripcion}', idCategoria='{id_categoria}', estado='{estado}' where id={id_product}"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        if id_product:
            sql = f"DELETE FROM piezas where idProducto={id_product}"
            cur.execute(sql)
            conn.commit()

            for pieza in request.get("piezas", []):
                desc_piezas = pieza["descripcion"]
                peso_piezas = int(pieza["peso"])
                horas_piezas = int(pieza["horas"])
                minutos_piezas = int(pieza["minutos"])
                sql = f"""INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto)
                        VALUES('{desc_piezas}','{peso_piezas}','{horas_piezas}','{minutos_piezas}','{id_product}');
                """
                cur.execute(sql)
                conn.commit()

            sql = f"DELETE FROM extra_producto where idProducto={id_product}"
            cur.execute(sql)
            conn.commit()

            for id_extra in request.get("extras", []):
                sql = f"""INSERT INTO extra_producto(idproducto, idextra)
                        VALUES('{id_product}','{id_extra}'');"""
                cur.execute(sql)
                conn.commit()
            return id_product
    except Error as e:
        print(str(e))
        return False
    finally:
        if conn:
            conn.close()
