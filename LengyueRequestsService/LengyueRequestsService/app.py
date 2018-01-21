import aioredis
import asyncio
import json5

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
        "requests_current": 0,
        "delay": []
    }

    current_config = {
        "max_requests": 500
    }
    callback_method = None
    config = None
    redis_host = None
    redis_password = None
    redis_port = None
    redis_db = None


    def default_controller(self, config, statue):
        """
        Default controller
        :param config: Service current config
        :param statue: Service current statue
        :return Target Config
        """
        return config

    def __init__(self):
        self.callback_method = self.default_controller
        self.loop = asyncio.get_event_loop()
        self.app = self
        pass

    def controller(self):
        """
        Decreator of Controller
        It can be set by users manually
        """
        def callback(handler):
            logger.info("Bind Controller -> %s" % handler.__name__)
            self.callback_method = handler

        return callback

    def run(self, redis_host="127.0.0.1", redis_port=6379, redis_password=None, redis_db=0, config=None):
        """
        Init LRS
        :param redis_host: redis host
        :param redis_port: redis service port
        :param redis_password: redis service password
        :param redis_db: redis cache db
        :param config: config filename
        """
        if config is not None:
            logger.info("Load config from file %s" % config)
            try:
                self.config = json5.loads(open(config, "r").read())
                self.redis_host = self.config["redis"]["host"]
                self.redis_port = self.config["redis"]["port"]
                self.redis_password = self.config["redis"]["password"]
                self.redis_db = self.config["redis"]["db"]
                self.current_config = json5.loads(open(self.config["process_config"], "r").read())
            except Exception:
                error_logger.warn("Load config failed")
                return
        else:
            self.redis_host = redis_host
            self.redis_port = redis_port
            self.redis_password = redis_password
            self.redis_db = redis_db

        logger.info("Config -> redis: %s@%s:%s db %s" % (redis_password or "None", redis_host, redis_port, redis_db))
        self.loop.run_until_complete(self.start_redis())
        tasks = [Process().work(self), statistic_listener(self)]
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.close()
        pass

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

