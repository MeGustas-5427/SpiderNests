import redis


class ServerPool:
    def __init__(self):
        dbc_redis = redis.Redis()
        dbc_redis.hset("nmb","gdx","wbd")
        print(dbc_redis.hget("nmb","gdx"))

        return

if __name__ == "__main__":
    s = ServerPool()