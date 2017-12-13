import redis
import classes.class_config

global_config = classes.class_config.config().read("global")
dbc = redis.Redis(db=5, host= global_config["db"]["redis"]["ip"], port= global_config["db"]["redis"]["port"], password= global_config["db"]["redis"]["password"])

def isAuth(token):
    if token == None or token == "":
        return False
    server_token = dbc.hget("user", "token")
    if server_token == None:
        return False
    if server_token.decode() == token:
        return True
    else:
        return False