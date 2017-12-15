# Author: Lengyue
# Filename: Lengyue-Requests.py
# Use: Core Requests
# Github: leng-yue
# License: MIT

import redis_helper
import asyncio
import redis
from aiohttp import ClientSession
import base64
import traceback

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
redis_conn = redis.StrictRedis(connection_pool=redis_pool)
redis_transformer = redis_helper.Helper()
redis_loop = asyncio.get_event_loop()
tasks = []

async def RedisListener():
    while True:
        try:
            task = redis_conn.rpop('queue:crawl')
            if task == None:
                await asyncio.sleep(0.01)
            else:
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

async def Crawl(task):
    async with ClientSession() as session:
        #print(task)
        response = "-1"
        content = "-1"
        try:
            if task["method"].lower() == "get":
                async with session.get(task["url"], headers= task["headers"], proxy= task["proxy"]) as response:
                    content = await response.read()
            if task["method"].lower() == "post":
                async with session.post(task["url"], headers= task["headers"], proxy= task["proxy"],data= base64.b64decode(task["data"])) as response:
                    content = await response.read()
            if task["method"].lower() == "head":
                async with session.head(task["url"], headers= task["headers"], proxy= task["proxy"]) as response:
                    content = await response.read()
            #print(content)
        except:
            traceback.print_exc()

            #print(response)
    return {
        "response": response,
        "content": content,
        "id": task["id"]
    }

def Callback(info):
    result = info.result()
    if result["response"] == "-1":
        ans = {
            "id": result["id"],
            "status": "600"
        }
    else:
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
    ans = redis_transformer.Transform(ans)
    for i in ans.keys():
        redis_conn.hset(result["id"], i, ans[i])
    redis_conn.publish("guangbo", result["id"])
    #print(result["response"].headers)

if __name__ == "__main__":
    task = asyncio.ensure_future(RedisListener())
    #loop.run_until_complete(asyncio.wait(tasks))
    redis_loop.run_forever()