import gevent
import time
from queue import Queue
from gevent import monkey
import traceback
import redis
import requests

monkey.patch_socket()
monkey.patch_os()
monkey.patch_time()
monkey.patch_subprocess()

dbc = redis.Redis()
dbc_write = redis.Redis(db=1)
lock = []
def crawler():
    while True:
        try:
            while True:
                key = dbc.randomkey()
                if key != None and key not in lock:
                    info = dbc.hgetall(key)
                    if b"finish" in info:
                        lock.append(key)
                        dbc.delete(key)
                        print(info)
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
            if ans["proxies"]["https"] == "":
                ans["proxies"]["https"] = None
            if ans["proxies"]["http"] == "":
                ans["proxies"]["http"] = None
            print(ans)
            method = ans["method"]

            if method.lower() == "get":
                ret = requests.get(ans["url"],proxies= ans["proxies"], headers= ans["headers"])
            if method.lower() == "post":
                ret = requests.get(ans["url"],data=ans["data"],proxies= ans["proxies"], headers= ans["headers"])

            headers = {}
            for i in ret.headers.keys():
                headers[i] = ret.headers.get(i)
            task = {
                "method": "return",
                "requestid": ans["requestid"],
                "state": ret.status_code,
                "url": ret.url,
                "headers": headers,
                "content": ret.content,
                "finish":"1"
            }

            for i in task.keys():
                if type(task[i]) == type({}):
                    for j in task[i].keys():
                        dbc_write.hset(key, i + "::" + j, task[i][j])
                else:
                    dbc_write.hset(key, i, task[i])

            gevent.sleep(0.1)
        except:
            traceback.print_exc()

if __name__ == "__main__":
    l = []
    for i in range(10):
        l.append(gevent.spawn(crawler()))

    gevent.joinall(l)
