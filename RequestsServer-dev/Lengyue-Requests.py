# Author: Lengyue
# Filename: Lengyue-Requests.py
# Use: Core Requests
# Github: leng-yue
# License: MIT

import redis_helper
import asyncio
from aiohttp import ClientSession
import base64
import traceback
import time
import psutil
import time
import json
import redis

#读入一车数据
config = json.loads(open("./config.json","r").read())
redis_pool = redis.ConnectionPool(host= config["redis"]["ip"], port= config["redis"]["port"], password= config["redis"]["password"], db=0)
redis_conn = redis.StrictRedis(connection_pool=redis_pool)
redis_transformer = redis_helper.Helper()
redis_loop = asyncio.get_event_loop()
tasks = []
statistic = {
    "requests_total":0,
    "delay":[]
}
#统计函数
async def StatisticListener():
    dbc = redis.Redis(db=4, host=config["redis"]["ip"], port=config["redis"]["port"],
                      password=config["redis"]["password"])
    last = 0
    #10s统计
    while True:
        try:
            mem = psutil.virtual_memory()
            net_io = psutil.net_io_counters()
            now = net_io.bytes_sent + net_io.bytes_recv
            delay = 0
            #计算平均延迟
            for i in statistic["delay"]:
                delay += i
            if len(statistic["delay"]) != 0:
                delay /= len(statistic["delay"])
            else:
                delay = 0
            statistic["delay"] = []
            info = {
                "serverid": config["serverid"],
                "type": 0,
                "cpu": {
                    "cores_num": psutil.cpu_count(),
                    "useage": psutil.cpu_percent(1)
                },
                "memory": {
                    "max": mem.total,
                    "used": mem.used,
                    "free": mem.free
                },
                "network": {
                    "average_10_seconds": (now - last) / 10
                },
                "requests": {
                    "average_requests_num": statistic["requests_total"] / 10,
                    "average_delay": delay,  # ms
                },
                "timestamp": time.time()
            }
            statistic["requests_total"] = 0
            last = now
            ans = redis_transformer.Transform(info)
            for i in ans.keys():
                dbc.hset(config["serverid"], i, ans[i])
            # print(json.dumps(info))
            await asyncio.sleep(10)
        except:
            traceback.print_exc()

#监听队列
async def RedisListener():
    while True:
        try:
            task = redis_conn.rpop('queue:crawl')
            if task == None:
                #没有就休息 不能死循环 不然会阻塞
                await asyncio.sleep(0.01)
            else:
                #读取任务信息
                temp = redis_conn.hgetall(task)
                arr = {}
                for i in temp.keys():
                    arr[i.decode()] = temp[i].decode()
                if arr["proxy"] == "None":
                    arr["proxy"] = None
                give_task = redis_transformer.DeTransform(arr)
                task = asyncio.ensure_future(Crawl(give_task))
                task.add_done_callback(Callback)
                tasks.append(task)
        except:
            traceback.print_exc()

#请求主函数
async def Crawl(task):
    async with ClientSession() as session:
        #print(task)
        response = "-1"
        content = "-1"
        try:
            statistic["requests_total"] += 1
            start = int(time.time() * 1000)
            #判断请求类别
            if task["method"].lower() == "get":
                async with session.get(task["url"], headers= task["headers"], proxy= task["proxy"]) as response:
                    content = await response.read()
            if task["method"].lower() == "post":
                async with session.post(task["url"], headers= task["headers"], proxy= task["proxy"],data= base64.b64decode(task["data"])) as response:
                    content = await response.read()
            if task["method"].lower() == "head":
                async with session.head(task["url"], headers= task["headers"], proxy= task["proxy"]) as response:
                    content = await response.read()
            end = int(time.time() * 1000)
            statistic["delay"].append(end - start)
            #print(content)
        except:
            traceback.print_exc()

            #print(response)
    return {
        "response": response,
        "content": content,
        "id": task["id"]
    }

#回调主函数
def Callback(info):
    result = info.result()
    #异常状态
    if result["response"] == "-1":
        ans = {
            "id": result["id"],
            "status": "600"
        }
    else:
        #统计数据
        ans = {
            "id": result["id"],
            "status": result["response"].status,
            "url": result["response"].url,
            "content":base64.b64encode(result["content"]),
            "headers":{}
        }
        for i in result["response"].headers.keys():
            if i in ans["headers"]:
                if type(ans["headers"][i]) == type([]):
                    ans["headers"][i].append(result["response"].headers[i])
                else:
                    temp = ans["headers"][i]
                    ans["headers"][i] = [temp]
                    ans["headers"][i].append(result["response"].headers[i])
            else:
                ans["headers"][i] = result["response"].headers[i]
    #降纬
    ans = redis_transformer.Transform(ans)
    for i in ans.keys():
        redis_conn.hset(result["id"], i, ans[i])
    redis_conn.publish("guangbo", result["id"])
    #print(result["response"].headers)

if __name__ == "__main__":
    asyncio.ensure_future(StatisticListener())
    asyncio.ensure_future(RedisListener())
    #loop.run_until_complete(asyncio.wait(tasks))
    redis_loop.run_forever()