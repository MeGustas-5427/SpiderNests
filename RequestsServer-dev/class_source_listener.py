import psutil
import time
import json
import redis
import gevent

config = json.loads(open("./config.json","r").read())
dbc = redis.Redis(db=4, host= config["redis"]["ip"], port= config["redis"]["port"], password= config["redis"]["password"])

class listen:
    def __init__(self):
        last = 0
        while True:
            mem = psutil.virtual_memory()
            net_io = psutil.net_io_counters()
            now = net_io.bytes_sent + net_io.bytes_recv
            info = {
                "serverid":config["serverid"],
                "type":0,
                "cpu":{
                    "cores_num":psutil.cpu_count(),
                    "useage":psutil.cpu_percent(1)
                },
                "memory":{
                    "max": mem.total,
                    "used": mem.used,
                    "free": mem.free
                },
                "network":{
                    "average_10_seconds": (now - last)/10
                },
                "timestamp":time.time()
            }
            last = now
            dbc.set(config["serverid"],json.dumps(info))
            #print(json.dumps(info))
            gevent.sleep(10)