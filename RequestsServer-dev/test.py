import redis
import random
import hashlib
from LengyueRequestsService.redis_packer import Packer
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
helper = Packer()
for i in range(100):


    key = hashlib.md5(str(random.random()).encode()).hexdigest()
    ans = helper.pack({
        "method":"get",
        "url":"http://zhihu.com",
        "headers":{
            "cookie":"NMB",
        },
        "data":"base64ed",
        "id":key,
        "proxy":None,
    })

    for i in ans.keys():
        r.hset("tasksList:" + key, i, ans[i])
    r.lpush('queue:crawl', key)
