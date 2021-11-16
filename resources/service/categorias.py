import psycopg2.extras
from sqlite3 import Error
from database.connection import create_connection


def get_all_categories():
    conn = create_connection()
    sql = f"SELECT * FROM categorias ORDER BY categoria ASC;"

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


def add_category(request):
    conn = create_connection()
    sql = f"INSERT INTO categorias(categoria) VALUES ('{request['categoria'].upper()}') RETURNING id;"

    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        id_categoria = cur.fetchone()[0]
        return id_categoria
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()


def update_category(_id, request):
    conn = create_connection()
    sql = f"UPDATE categorias SET categoria='{request['categoria'].upper()}' WHERE id='{_id}';"

    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return
    except Error as e:
        print(str(e))
    finally:
        if conn:
            conn.close()
