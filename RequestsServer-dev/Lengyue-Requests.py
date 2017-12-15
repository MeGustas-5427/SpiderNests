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

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)
helper = redis_helper.helper()
loop = asyncio.get_event_loop()
tasks = []

async def RedisListener():
    while True:
        task = r.rpop('queue:crawl')
        if task == None:
            await asyncio.sleep(0.1)
        else:
            print(task)
            give_task = {
                "url":"http://zhihu.com",
                "id":task
            }
            task = asyncio.ensure_future(Crawl(give_task))
            task.add_done_callback(Callback)
            tasks.append(task)

async def Crawl(task):
    async with ClientSession() as session:
        async with session.get(task["url"]) as response:
            content = await response.read()
            #print(response)
    return {
        "response": response,
        "content": content,
        "id": task["id"]
    }

def Callback(info):
    result = info.result()
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
    ans = helper.Transform(ans)
    for i in ans.keys():
        r.hset(result["id"],i,ans[i])
    r.publish("guangbo", result["id"])
    #print(result["response"].headers)

task = asyncio.ensure_future(RedisListener())

#loop.run_until_complete(asyncio.wait(tasks))
loop.run_forever()