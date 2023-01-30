import os

import redis


def create_redis_connection():
    pool = redis.ConnectionPool(host=os.getenv('DATABASE_HOST'),
                                port=6379,
                                db=0,
                                password=os.getenv('DATABASE_PASSWORD'))
    return redis.Redis(connection_pool=pool)

