import sqlite3
from sqlite3 import Error

import psycopg2


def create_connection():
    conn = None

    try:
        # conn = sqlite3.connect("database/doblev3d.db")
        conn = psycopg2.connect(user="ymppotlgjjebjq",
                                password="faceef51455cac7509f7d4a3d85e1912b60cbd1916a1199dd58b3c08960b6cac",
                                database="ddgkh0j1qnn483",
                                host="ec2-3-209-65-193.compute-1.amazonaws.com",
                                port="5432")
    except Error as e:
        print(f"Error connecting to database: {str(e)}")
    return conn
