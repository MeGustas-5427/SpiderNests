import redis
rdp = redis.ConnectionPool(host='127.0.0.1', port=6379)
dbc = redis.StrictRedis(connection_pool=rdp, db=9)
a = {
    "nmb":"s",
    "hh":["hhh"]
}
dbc.set("a",a)
print(dbc.get("a")["nmb"])
