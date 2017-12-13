import redis
import time
import random
from hashlib import md5

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
    },
    "finish":"1"
}

for i in task.keys():
    if type(task[i])==type({}):
        for j in task[i].keys():
            dbc.hset(key, i+"::"+j, task[i][j])
    else:
        dbc.hset(key,i,task[i])

while True:
    info = dbc_write.hgetall(key)
    if info!={} and b"finish" in info:
        dbc_write.delete(key)
        break

ans = {}
for i in info.keys():
    if "::" in i.decode():
        a,b = i.decode().split("::")
        if not a in ans.keys():
            ans[a] = {}
        ans[a][b] = info[i].decode()
    else:
        ans[i.decode()] = info[i].decode()

print(ans)
