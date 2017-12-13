from flask import Flask
import json
from classes import class_logger, class_config
app = Flask(__name__)

#Load Configs
config = class_config.config().read("global")
#Init Logger
logger = class_logger.logger(config["log"]["file"])
logger_main = logger.getLogger("Main-Process")
logger_main.info("--------------------Start Init System--------------------")
#Load Modules
logger_main.info("Flask Settings -> " + str(config["Flask_Settings"]))
logger_main.info("Starting to load Modules")
for i in config["Modules"]:
    logger_main.info(i)
    logger_main.info("--------------------Start loading " + "%s.%s" % (i["path"], i["name"]) + "--------------------")
    logger_main.info("Loading %s Blueprints" % (len(i["blueprints"])))
    temp_module = __import__("%s.%s" % (i["path"], i["name"]), fromlist= i["blueprints"])
    for blueprint in i["blueprints"]:
        logger_main.info("Loading " + blueprint)
        app.register_blueprint(eval("temp_module.%s" % blueprint))
    logger_main.info("--------------------Finish loading " + "%s.%s" % (i["path"], i["name"]) + "--------------------")
logger_main.info("Loaded Modules")
logger_main.info("--------------------Finish Init System--------------------")
if __name__ == "__main__":
    app.run(host= config["Flask_Settings"]["host"], port= config["Flask_Settings"]["port"])