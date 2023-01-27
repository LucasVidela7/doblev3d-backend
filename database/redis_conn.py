import redis


def create_redis_connection():
    # TODO asignar a variables de entorno
    pool = redis.ConnectionPool(host='doblev3d.duckdns.org',
                                port=6379,
                                db=0,
                                password="Joaquin.2018")
    return redis.Redis(connection_pool=pool)

