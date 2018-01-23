import hashlib
import random
import asyncio
from .log import logger, error_logger
from aiohttp import ClientSession
import base64
import time
import traceback
import json

"""
Crawl Core
"""
class CrawlPool:
    def __init__(self, app):
        self.app = app
        self.pool = {}
        self.lock = asyncio.Lock()
        self.target = 0
        pass

    async def work(self):
        """
        Start a pool
        :return:
        """
        await self.lock.acquire()
        alive_iterators = len(self.pool.keys())
        change_value = self.app.current_config["max_requests"] - alive_iterators
        if change_value != 0:
            logger.info("Modify Crawl_nums %i to %i Start" % (alive_iterators, self.app.current_config["max_requests"]))
            if change_value > 0:
                for i in range(change_value):
                    self.app.loop.create_task(self.crawl_persist())
                self.lock.release()
            else:
                self.target = abs(change_value)
            logger.info("Modify Crawl_nums %i to %i Succeed" % (alive_iterators, self.app.current_config["max_requests"]))
        else:
            self.lock.release()
        self.app.loop.call_later(self.app.config["control_interval"], self.app.loop.create_task, self.work())

    async def count(self):
        """
        Counter
        """
        self.target -= 1
        if self.target == 0:
            if self.lock.locked():
                self.lock.release()

    async def _iter(self):
        """
        Iteration
        :return:
        """
        reg_id = hashlib.md5(str(random.random()).encode()).hexdigest()
        self.pool[reg_id] = {
            "statue": "alive"
        }
        # logger.info("Iterator %s Starts" % reg_id)
        while True and self.pool[reg_id]["statue"] == "alive" and self.target == 0:
            task = await self.app.Queue.get()
            yield task
        del self.pool[reg_id]
        # logger.info("Iterator %s Exits" % reg_id)
        await self.count()

    async def crawl_persist(self):
        """
        Async - Crawl
        :return:
        """
        _iter = self._iter()
        async for task in _iter:
            self.app.statistic["requests_current"] += 1
            response = "-1"
            content = "-1"
            try:
                self.app.statistic["requests_total_made"] += 1
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
            await self.app.redis.set("crawl:result:" + final_info["task_id"], json.dumps(final_info).encode())
            await self.app.redis.expire("crawl:result:" + final_info["task_id"], 300)
            await self.app.redis.publish("crawl:finish", final_info["task_id"])
            self.app.statistic["requests_current"] -= 1
            self.app.statistic["requests_total_finish"] += 1