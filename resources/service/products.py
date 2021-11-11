import sqlite3
from datetime import datetime
from sqlite3 import Error
from database.connection import create_connection


def insert_product(request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    fecha_creacion = datetime.now().strftime('%x')  # 11/11/2021

    data = (descripcion, id_categoria, fecha_creacion)
    conn = create_connection()
    sql = """INSERT INTO productos(descripcion,id_categoria, fecha_creacion)
            VALUES(?,?,?);
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(str(e))
        return False
    finally:
        if conn:
            cur.close()
            conn.close()


def select_product_by_id(_id):
    conn = create_connection()
    sql = f"SELECT * FROM productos WHERE id= {_id}"

    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        product = dict(cur.fetchone())
        return product
    except Error as e:
        print(str(e))
    finally:
        if conn:
            cur.close()
            conn.close()


def get_all_products():
    conn = create_connection()
    sql = f"SELECT * FROM productos"

    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        products = cur.fetchall()
        return [dict(p) for p in products]
    except Error as e:
        print(str(e))
    finally:
        if conn:
            cur.close()
            conn.close()
