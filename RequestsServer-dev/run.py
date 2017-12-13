import gevent
import class_source_listener as listener
from gevent import monkey
import traceback
import redis
import requests
import json
import base64

monkey.patch_socket()
monkey.patch_os()
monkey.patch_time()
monkey.patch_subprocess()

dbc = redis.Redis()
dbc_write = redis.Redis(db=1)
lock = []
def crawler(t):
    while True:
        try:
            while True:
                key = dbc.randomkey()
                if key != None and key not in lock:
                    lock.append(key)
                    ans = json.loads(dbc.get(key).decode())
                    print(t,ans)
                    break
                gevent.sleep(0.01)

            if ans["proxies"]["https"] == "":
                ans["proxies"]["https"] = None
            if ans["proxies"]["http"] == "":
                ans["proxies"]["http"] = None
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
                "content": base64.b64encode(ret.content).decode(),
            }
            dbc_write.set(key, json.dumps(task))
            dbc.delete(key)
            gevent.sleep(0.01)
        except:
            traceback.print_exc()

if __name__ == "__main__":
    l = []
    gevent.spawn(listener.listen)
    for i in range(20):
        l.append(gevent.spawn(crawler,i))

    gevent.joinall(l)
