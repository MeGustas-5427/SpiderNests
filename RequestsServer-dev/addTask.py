import redis
import time
import random
from hashlib import md5
import json

dbc = redis.Redis()
dbc_write = redis.Redis(db=1)
wait = []
for i in range(20):
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
        "url":"http://zhihu.com",
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
    wait.append(key)

s = time.time()
index = 0
while True:

    for key in wait:
        info = dbc_write.get(key)
        if info!=None:
            dbc_write.delete(key)
            index+=1
            print(json.loads(info.decode()))
    if index>18:
        print("cost %0.2f" % (time.time() - s))
        break
    if index % 10 == 0:
        print("cost %0.2f" % (time.time() - s))

s = time.time()
import requests
for i in range(20):
    requests.get("http://zhihu.com")
print("b cost %0.2f" % (time.time() - s))
