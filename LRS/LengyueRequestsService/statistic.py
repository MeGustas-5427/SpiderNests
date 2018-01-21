import psutil
import time
import traceback
import asyncio
import json
from .log import logger, error_logger

async def statistic_listener(app, last=0):
    """
    StatisticListener collect System info
    :param app: object of app
    """
    mem = psutil.virtual_memory()
    net_io = psutil.net_io_counters()
    now = net_io.bytes_sent + net_io.bytes_recv
    delay = sum(app.statistic["delay"])
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
            "average_requests_made": app.statistic["requests_total_made"] / 10,
            "average_requests_finish": app.statistic["requests_total_finish"] / 10,
            "average_delay": delay,  # ms
            "current_connections": app.statistic["requests_current"]
        },
        "current_config": app.current_config,
        "timestamp": time.time()
    }
    app.statistic["requests_total_made"] = 0
    app.statistic["requests_total_finish"] = 0
    logger.info("State: " + str(info))

    try:
        app.current_config = await app.app.callback_method(app.current_config, info)
        await app.redis.set("states:%s" % app.config["server_id"], json.dumps(info))
    except:
        error_logger.warn("Statistic Error" + "\r\n" + traceback.format_exc())
    finally:
        app.loop.call_later(10, app.loop.create_task, statistic_listener(app, now))