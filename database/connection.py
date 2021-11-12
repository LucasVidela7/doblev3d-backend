import sqlite3
from sqlite3 import Error

import psycopg2


def create_connection():
    conn = None

    try:
        # conn = sqlite3.connect("database/doblev3d.db")
        conn = psycopg2.connect(user="postgres", password="Joaquin.2018", database="doblev3d", host="localhost",
                                port="5432")
    except Error as e:
        print(f"Error connecting to database: {str(e)}")
    return conn
