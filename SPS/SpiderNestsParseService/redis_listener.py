import asyncio
import traceback
import aioredis
import base64
import json
from aioredis.pubsub import Receiver, AbcChannel
from .log import error_logger


class Listener:
    app = None
    redis = None

    async def reader(self, mpsc):
        """
        Sub to mpsc
        :param mpsc: mpsc
        """
        async for channel, msg in mpsc.iter():
            if not isinstance(channel, AbcChannel):
                error_logger.warn("Channel Reader Error, Type doesn't match")
            try:
                if msg.decode() in self.app.task_dict.keys():
                    content = await self.app.redis.get("crawl:result:" + msg.decode())
                    content = json.loads(content.decode())
                    if content["result"]["status"] != 600:
                        content["result"]["text"] = ""
                        content["result"]["content"] = base64.b64decode(content["result"]["content"].encode())
                        try:
                            content["result"]["text"] = content["result"]["content"].decode()
                        except:
                            pass
                    if self.app.task_dict[msg.decode()]["args"] is not None:
                        await self.app.task_dict[msg.decode()]["callback"](content,
                                                                       self.app.task_dict[msg.decode()]["args"])
                    else:
                        await self.app.task_dict[msg.decode()]["callback"](content)
                    self.app.task_dict.pop(msg.decode())
            except:
                error_logger.warn("Channel Reader Error" + "\r\n" + traceback.format_exc())

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
        mpsc = Receiver(loop=app.loop)
        asyncio.ensure_future(self.reader(mpsc), loop=app.loop)
        await self.redis.subscribe(mpsc.channel('crawl:finish'))
