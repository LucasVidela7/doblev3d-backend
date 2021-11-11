import sqlite3
from sqlite3 import Error
from database.connection import create_connection


def get_all_categories():
    conn = create_connection()
    sql = f"SELECT * FROM categorias"

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