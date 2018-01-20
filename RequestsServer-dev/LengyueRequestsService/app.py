import aioredis
import asyncio
import json

from LengyueRequestsService.log import *
from LengyueRequestsService.process import Process
from LengyueRequestsService.statistic import statistic_listener

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    logger.info("uvloop is unavaliable")

"""LRS Main Program"""


class LRS:
    pool = []
    redis = None
    statistic = {
        "requests_total": 0,
        "delay": []
    }
    current_config = {}

    def __init__(self, app, redis_host="127.0.0.1", redis_port=6379, redis_password=None, redis_db=0, config=None):
        """
        Init LRS
        :param app: controller
        :param redis_host: redis host
        :param redis_port: redis service port
        :param redis_password: redis service password
        :param redis_db: redis cache db
        """
        if config is not None:
            logger.info("Load config from file %s" % config)
            try:
                self.config = json.loads(open(config, "r").read())
                self.redis_host = self.config["redis"]["host"]
                self.redis_port = self.config["redis"]["port"]
                self.redis_password = self.config["redis"]["password"]
                self.redis_db = self.config["redis"]["db"]
                self.current_config = json.loads(open(self.config["process_config"], "r").read())
            except Exception:
                error_logger.warn("Load config failed")
        else:
            self.redis_host = redis_host
            self.redis_port = redis_port
            self.redis_password = redis_password
            self.redis_db = redis_db

        logger.info("Config -> redis: %s@%s:%s db %s" % (redis_password or "None", redis_host, redis_port, redis_db))
        self.loop = asyncio.get_event_loop()
        self.app = app
        self.Process = Process()
        self.loop.run_until_complete(self.start_redis())
        tasks = [self.process_control(), statistic_listener(self)]
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()
        pass

    async def process_control(self):
        """
        The multiprocess is not writtened
        """
        await self.Process.work(self)

    async def start_redis(self):
        """
        Start up redis
        """
        try:
            redis_pool = await aioredis.create_pool(
                    (self.redis_host, self.redis_port),
                    minsize=5, maxsize=10, password=self.redis_password or None,
                    db=self.redis_db, loop=self.loop
                )
            self.redis = await aioredis.Redis(redis_pool)
        except ConnectionRefusedError:
            error_logger.warn("Can not connect to Redis Server")

