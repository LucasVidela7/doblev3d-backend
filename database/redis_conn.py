import redis


def create_redis_connection():
    pool = redis.ConnectionPool(host='192.168.1.35', port=6379, db=0)
    return redis.Redis(connection_pool=pool)

