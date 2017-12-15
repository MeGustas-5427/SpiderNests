# coding=utf-8

import redis
import random
import hashlib
import redis_helper
import json

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
helper = redis_helper.Helper()
key = hashlib.md5(str(random.random()).encode()).hexdigest()
ans = helper.Transform({
		"method":"get",
		"url":"http://baidu.com",
		"headers":{
			"cookie":"NMB",
		},
		"data":"base64ed",
		"id":key,
		"proxy":None,
	})

for i in ans.keys():
    r.hset(key, i, ans[i])
r.lpush('queue:crawl', key)

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