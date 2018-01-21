import asyncio
from aiohttp import ClientSession
import traceback
import time
import aioredis
import base64
import json

from LengyueRequestsService.log import *


class Process:
    app = None
    redis = None

    def __init__(self):
        """
        Init Requests Process
        """
        pass

    async def work(self, app):
        """
        Start work, fetch tasks
        :param app: LRS object
        """
        self.app = app
        redis_pool = await aioredis.create_pool(
            (app.redis_host, app.redis_port),
            minsize=5, maxsize=10, password=app.redis_password or None,
            db=app.redis_db, loop=app.loop
        )
        self.redis = await aioredis.Redis(redis_pool)

        while True:
            try:
                task = await self.redis.brpop('crawl:queue')
                while self.app.statistic["requests_current"] > self.app.current_config["max_requests"]:
                    await asyncio.sleep(0.01)
                if task is not None:
                    give_task = json.loads(task[1].decode())
                    asyncio.ensure_future(self.crawl(give_task))
                else:
                    pass

            except:
                error_logger.warn("Process queue Error" + "\r\n" + traceback.format_exc())

    async def crawl(self, task):
        """
        Data crawler
        :param task: task dict
        """
        self.app.statistic["requests_current"] += 1
        response = "-1"
        content = "-1"
        try:
            self.app.statistic["requests_total"] += 1
            start = int(time.time() * 1000)
            async with ClientSession() as session:
                async with session.request(
                        method=task["method"].upper(),
                        url=task["url"],
                        proxy=task["proxy"] if "proxy" in task.keys() else None,
                        params=task["params"] if "params" in task.keys() else None,
                        data=task["data"] if "data" in task.keys() else None,
                        headers=task["headers"] if "headers" in task.keys() else None
                ) as crawl_response:
                    content = await crawl_response.read()
                    response = crawl_response

            end = int(time.time() * 1000)
            self.app.statistic["delay"].append(end - start)

        except:
            error_logger.warn("Requests Error" + "\r\n" + traceback.format_exc())

        final_info = {
            "task_id": task["task_id"],
            "task": task,
            "result": {}
        }
        if response == "-1":
            final_info["result"] = {
                "status": 600
            }
        else:
            try:
                final_info["result"] = {
                    "status": response.status,
                    "url": str(response.url),
                    "content": base64.b64encode(content).decode(),
                    "headers": {}
                }
                for i in response.headers.keys():
                    if i in final_info["result"]["headers"]:
                        if isinstance(final_info["result"]["headers"][i], list):
                            final_info["result"]["headers"][i].append(response.headers[i])
                        else:
                            temp = final_info["result"]["headers"][i]
                            final_info["result"]["headers"][i] = [temp]
                            final_info["result"]["headers"][i].append(response.headers[i])
                    else:
                        final_info["result"]["headers"][i] = response.headers[i]
            except:
                error_logger.warn("Requests Error, Failed to make final info")

        logger.info("Crawl ANS " + str(final_info))
        await self.app.redis.set("crawl:result:" + final_info["task_id"], json.dumps(final_info).encode())
        await self.app.redis.expire("crawl:result:" + final_info["task_id"], 300)
        await self.app.redis.publish("crawl:finish", final_info["task_id"])
        self.app.statistic["requests_current"] -= 1
