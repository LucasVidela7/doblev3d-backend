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