from LengyueRequestsService.log import *
from LengyueRequestsService.app import LRS


class Controller:
    callback_method = None

    """Deafult controller
    :param config: Service current config
    :return Target Config
    """
    def deafult_controller(self, config, state):
        return config

    def __init__(self):
        self.callback_method = self.deafult_controller
        pass

    """Decreator of Controller
    It can be set by users manually
    """
    def reciver(self):
        def callback(handler):
            logger.info("Bind Controller -> %s" % handler.__name__)
            self.callback_method = handler
        return callback

    """Run Controller
    :param redis_host: redis host
    :param redis_port: redis service port
    :param redis_password: redis service password
    :param redis_db: redis cache db
    """
    def run(self, redis_host="127.0.0.1", redis_port=6379, redis_password="", redis_db=0, config=None):
        logger.info("Try to start up LRS service")
        LRS(app=self, redis_host=redis_host, redis_port=redis_port, redis_password=redis_password,
            redis_db=redis_db, config=config)