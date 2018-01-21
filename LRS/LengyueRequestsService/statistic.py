import psutil
import time
import traceback
import asyncio
import json
from LengyueRequestsService.log import *


async def statistic_listener(app):
    """
    StatisticListener collect System info
    :param app: object of app
    """
    last = 0
    while True:
        try:
            mem = psutil.virtual_memory()
            net_io = psutil.net_io_counters()
            now = net_io.bytes_sent + net_io.bytes_recv
            delay = 0
            # Calculate average delay
            for i in app.statistic["delay"]:
                delay += i
            if len(app.statistic["delay"]) != 0:
                delay /= len(app.statistic["delay"])
            else:
                delay = 0
                app.statistic["delay"] = []
            info = {
                "server_id": app.config["server_id"],
                "type": 0,
                "cpu": {
                    "cores_num": psutil.cpu_count(),
                    "useage": psutil.cpu_percent(1)
                },
                "memory": {
                    "max": mem.total,
                    "used": mem.used,
                    "free": mem.free
                },
                "network": {
                    "average_10_seconds": (now - last) / 10
                },
                "requests": {
                    "average_requests_num": app.statistic["requests_total"] / 10,
                    "average_delay": delay,  # ms
                    "current_connections": app.statistic["requests_current"]
                },
                "current_config": app.current_config,
                "timestamp": time.time()
            }
            app.statistic["requests_total"] = 0
            last = now
            logger.info("State: " + str(info))
            app.current_config = await app.app.callback_method(app.current_config, info)

            await app.redis.set("states:%s" % app.config["server_id"], json.dumps(info))
            await asyncio.sleep(10)
        except:
            error_logger.warn("Statistic Error" + "\r\n" + traceback.format_exc())