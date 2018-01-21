import redis
import random
import hashlib
import json
import base64
from LengyueRequestsService.redis_packer import Packer
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
helper = Packer()

for i in range(1000):
    key = hashlib.md5(str(random.random()).encode()).hexdigest()
    task = json.dumps({
        "task_id": key,
        "method": "GET",
        "url": "https://zhihu.com",
        "headers": {
        },
        "params": {
            "ver": -1
        },
        "data": None,
        "proxy": None,
    })

    r.lpush('crawl:queue', base64.b64encode(task.encode()))
p = r.pubsub()
p.subscribe("crawl:finish")
n = 0
while True:
    i = p.get_message()
    if i != None:
        if i["type"] == "message":
            j = base64.b64decode(r.get("crawl:result:" + i["data"].decode())).decode()
            j = json.loads(j)
            print(base64.b64decode(j["result"]["content"]).decode())
            n += 1
            print("Current Recv", n)