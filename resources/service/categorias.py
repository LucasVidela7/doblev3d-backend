import psycopg2.extras
from sqlite3 import Error
from database.connection import create_connection


def get_all_categories():
    conn = create_connection()
    sql = f"SELECT * FROM categorias"

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        products = cur.fetchall()
        return [dict(p) for p in products]
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()
