import psycopg2.extras
from sqlite3 import Error
from database.connection import create_connection


def get_all_extras():
    conn = create_connection()
    sql = f"SELECT * FROM extras"

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        extras = cur.fetchall()
        return [dict(e) for e in extras]
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()


def select_extras_by_id(id_product):
    conn = create_connection()
    sql = f"SELECT * FROM extra_producto WHERE idproducto= {id_product}"

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        extras = list(cur.fetchall())

        list_extras = []
        for e in extras:
            new_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            sql = f"SELECT * FROM extras WHERE id= {e['idextra']}"
            new_cur.execute(sql)
            list_extras.append(dict(new_cur.fetchone()))
        return list_extras
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()
