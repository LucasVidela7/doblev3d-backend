import os
from sqlite3 import Error

import psycopg2


def create_connection():
    conn = None

    try:
        conn = psycopg2.connect(user=os.getenv('DATABASE_USER'),
                                password=os.getenv('DATABASE_PASSWORD'),
                                database=os.getenv('DATABASE_DB'),
                                host=os.getenv('DATABASE_HOST'),
                                port="5432")
    except Error as e:
        print(f"Error connecting to database: {str(e)}")
    return conn
