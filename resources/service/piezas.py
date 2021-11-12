import sqlite3
from sqlite3 import Error
from database.connection import create_connection


def select_piezas_by_id_product(_id):
    conn = create_connection()
    sql = f"SELECT * FROM piezas WHERE idProducto= {_id}"

    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        piezas = cur.fetchall()
        return [dict(p) for p in piezas]
    except Error as e:
        print(str(e))
    finally:
        if conn:
            cur.close()
            conn.close()