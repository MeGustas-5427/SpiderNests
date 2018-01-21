import aioredis
import asyncio
import json5
import hashlib
import random
from .redis_listener import Listener
from .log import logger, error_logger

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    logger.info("uvloop is unavaliable")


class SPS:
    main_entrance = None
    config = None
    redis_host = None
    redis_password = None
    redis_port = None
    redis_db = None
    redis = None
    task_dict = {}

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def requests(self, url, callback, method="GET", proxy=None, params=None, data=None, headers=None, args=None):
        """
        Make a request to LRS
        :param url: url
        :param callback: callback func
        :param method: method
        :param proxy: proxy
        :param params: params for get
        :param data: data for post
        :param headers: headers
        :return:
        """
        key = hashlib.md5((url + str(random.random())).encode()).hexdigest()
        task = json5.dumps({
            "task_id": key,
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": data,
            "proxy": proxy
        }).encode()
        self.task_dict[key] = {
            "callback": callback,
            "args": args
        }
        asyncio.ensure_future(self.redis.lpush('crawl:queue', task))

    def main(self):
        """
        Decorator of main
        """
        def callback(handler):
            logger.info("Bind Main Program -> %s" % handler.__name__)
            self.main_entrance = handler
        return callback

    def run(self, redis_host="127.0.0.1", redis_port=6379, redis_password=None, redis_db=0, config=None):
        """
        Init SPS
        :param redis_host: redis host
        :param redis_port: redis service port
        :param redis_password: redis service password
        :param redis_db: redis cache db
        :param config: config filename
        """
        if self.main_entrance is None:
            error_logger.warn("Undefined main_entrance")
            return
        if config is not None:
            logger.info("Load config from file %s" % config)
            try:
                self.config = json5.loads(open(config, "r").read())
                self.redis_host = self.config["redis"]["host"]
                self.redis_port = self.config["redis"]["port"]
                self.redis_password = self.config["redis"]["password"]
                self.redis_db = self.config["redis"]["db"]
            except Exception:
                error_logger.warn("Load config failed")
                return
        else:
            self.redis_host = redis_host
            self.redis_port = redis_port
            self.redis_password = redis_password
            self.redis_db = redis_db

        logger.info("Config -> redis: %s@%s:%s db %s" % (
            self.redis_password or "None",
            self.redis_host,
            self.redis_port,
            self.redis_db
        )
                    )
        self.loop.run_until_complete(self.start_redis())
        asyncio.ensure_future(Listener().work(self), loop=self.loop)
        self.loop.run_until_complete(self.main_entrance())
        self.loop.run_forever()

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

