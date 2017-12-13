import redis
import time
import random
from hashlib import md5
import json

dbc = redis.Redis()
dbc_write = redis.Redis(db=1)

key = md5((str(time.time())+str(random.random())).encode()).hexdigest()
"""
{
    "method":"get",
    "url":"http://baidu.com",
    "headers":{
        "cookie":"NMB",
    },
    "data":"base64ed",
    "content":"base64ed",
    "requestid":"hash",
    "proxies":{
        "http":"",
        "https":""
    }   
}
"""

task = {
    "method":"get",
    "url":"http://111.230.227.130:8100/parse?token=test404&key=FFFF0000000001676215&scene=activity",
    "headers":{
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    },
    "data":"",
    "content":"",
    "requestid":key,
    "proxies":{
        "http":"",
        "https":""
    }
}

dbc.set(key,json.dumps(task))

while True:
    info = dbc_write.get(key)
    if info!=None:
        dbc_write.delete(key)
        break

print(json.loads(info.decode()))
