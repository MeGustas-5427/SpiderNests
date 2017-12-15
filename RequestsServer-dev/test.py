# coding=utf-8

import redis
import random
import hashlib
import redis_helper
import json

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
helper = redis_helper.helper()

while True:
    input_info = str(input("publish:"))
    if input_info  == 'over':
        print('停止发布')
        break
    r.lpush('queue:crawl', hashlib.md5(str(random.random()).encode()).hexdigest())

    sub = r.pubsub()
    sub.subscribe("guangbo")
    sub.listen()
    while True:
        msg = sub.parse_response(block=False, timeout=60)
        if len(msg) == 3 and type(msg[2]) == type(b"") and len(msg[2]) == 32:
            temp = r.hgetall(msg[2])
            r.delete(msg[2])
            arr = {}
            for i in temp.keys():
                arr[i.decode()] = temp[i].decode()
            print(json.dumps(helper.DeTransform(arr)))