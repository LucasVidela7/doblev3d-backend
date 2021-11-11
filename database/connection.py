import sqlite3
from sqlite3 import Error


def create_connection():
    conn = None

    try:
        conn = sqlite3.connect("database/doblev3d.db")
    except Error as e:
        print(f"Error connecting to database: {str(e)}")
    return conn
