import psycopg2.extras
from database.connection import create_connection
from sqlite3 import Error


def execute_sql(sql):
    conn = create_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        conn.commit()
        return cur, conn
    except Error as e:
        print(str(e))


def insert_sql(sql, key=None):
    cur, conn = execute_sql(sql)
    if key:
        return  dict(cur.fetchone())[key]
    conn.close()
    return


def update_sql(sql):
    cur, conn = execute_sql(sql)
    conn.close()
    return


def delete_sql(sql):
    cur, conn = execute_sql(sql)
    conn.close()
    return


def select_multiple(sql):
    cur, conn = execute_sql(sql)
    query = [dict(q) for q in cur.fetchall()]
    conn.close()
    return query


def select_first(sql):
    cur, conn = execute_sql(sql)
    query = dict(cur.fetchone())
    conn.close()
    return query
