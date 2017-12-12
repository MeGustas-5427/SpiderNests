#encoding=utf-8
# 配置日志信息
import logging

class logger:
    def __init__(self,filename):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-40s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=filename,
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(name)-25s | %(levelname)-8s| %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def getLogger(self,name):
        return logging.getLogger(name)
