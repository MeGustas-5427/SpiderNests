import asyncio
from aiohttp import ClientSession
import base64
import traceback
import time
import aioredis

from LengyueRequestsService.log import *
from LengyueRequestsService.redis_packer import Packer


class Process:
    app = None


    def __init__(self):
        pass

    async def work(self, app):
        self.app = app
        redis_pool = await aioredis.create_pool(
            (app.redis_host, app.redis_port),
            minsize=5, maxsize=10, password=app.redis_password or None,
            db=app.redis_db, loop=app.loop
        )
        self.redis = await aioredis.Redis(redis_pool)
        while True:
            try:
                task = await self.redis.brpop('queue:crawl')

                if task is not None:
                    temp = await app.redis.hgetall(b"tasksList:" + task[1])
                    await self.redis.delete(b"tasksList:" + task[1])
                    arr = {}
                    for i in temp.keys():
                        arr[i.decode()] = temp[i].decode()
                    if arr["proxy"] == "None":
                        arr["proxy"] = None
                    give_task = Packer().unpack(arr)
                    asyncio.ensure_future(self.Crawl(give_task))
                else:

                    pass

            except:
                error_logger.warn("Process queue Error" + "\r\n" + traceback.format_exc())

    async def Crawl(self, task):
        async with ClientSession() as session:
            # print(task)
            response = "-1"
            content = "-1"
            try:
                self.app.statistic["requests_total"] += 1
                start = int(time.time() * 1000)
                # 判断请求类别
                if task["method"].lower() == "get":
                    async with session.get(task["url"], headers=task["headers"], proxy=task["proxy"]) as response:
                        content = await response.read()
                if task["method"].lower() == "post":
                    async with session.post(task["url"], headers=task["headers"], proxy=task["proxy"],
                                            data=base64.b64decode(task["data"])) as response:
                        content = await response.read()
                if task["method"].lower() == "head":
                    async with session.head(task["url"], headers=task["headers"], proxy=task["proxy"]) as response:
                        content = await response.read()
                end = int(time.time() * 1000)
                self.app.statistic["delay"].append(end - start)
                # print(content)
            except:
                traceback.print_exc()

                # print(response)
        result = {
            "response": response,
            "content": content,
            "id": task["id"]
        }
        if result["response"] == "-1":
            ans = {
                "id": result["id"],
                "status": "600"
            }
        else:
            # 统计数据
            ans = {
                "id": result["id"],
                "status": result["response"].status,
                "url": str(result["response"].url),
                "content": base64.b64encode(result["content"]),
                "headers": {}
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
        # 降纬
        ans = Packer().pack(ans)
        logger.info("Crawl ANS " + str(ans))
        await self.app.redis.hmset_dict("result:" + result["id"], ans)
        # 两分钟不获取 回收
        await self.app.redis.expire("result:" + result["id"], 120)
        await self.app.redis.publish("guangbo", result["id"])