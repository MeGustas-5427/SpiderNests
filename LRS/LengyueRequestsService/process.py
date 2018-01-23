import traceback
import aioredis
import json
from .log import error_logger


class Process:
    app = None
    redis = None

    async def connect_redis(self):
        redis_pool = await aioredis.create_pool(
            (self.app.redis_host, self.app.redis_port),
            minsize=5, maxsize=10, password=self.app.redis_password or None,
            db=self.app.redis_db, loop=self.app.loop
        )
        self.redis = await aioredis.Redis(redis_pool)


    def __init__(self, app):
        self.app = app
        app.loop.run_until_complete(self.connect_redis())

    async def work(self):
        """
        Redis - Queue
        """
        try:
            task = await self.redis.brpop('crawl:queue')
            if task is not None:
                give_task = json.loads(task[1].decode())
                await self.app.Queue.put(give_task)
            else:
                pass
        except:
            error_logger.warn("Process queue Error" + "\r\n" + traceback.format_exc())
        self.app.loop.create_task(self.work())