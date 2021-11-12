from sqlite3 import Error
from database.connection import create_connection
import psycopg2.extras


def select_piezas_by_id_product(_id):
    conn = create_connection()
    sql = f"SELECT * FROM piezas WHERE idProducto= {_id}"

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        piezas = cur.fetchall()
        return [dict(p) for p in piezas]
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()
