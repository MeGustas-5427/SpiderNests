# servercore.py
# Author:Lengyue
# manage users

from flask import Blueprint, request
import redis
from classes import class_config, class_auth
import logging
import json

servercore = Blueprint('servercore', __name__,
                        template_folder='templates')

config = class_config.config().read("servercore")
global_config = class_config.config().read("global")
logger = logging.getLogger(config["log"]["name"])
dbc = redis.Redis(db=4, host= global_config["db"]["redis"]["ip"], port= global_config["db"]["redis"]["port"], password= global_config["db"]["redis"]["password"])

# 获取服务器列表api
# 请求方式 GET
# 请求内容
# token -> 令牌
# errcode -> 0 成功
# errcode -> 1 token错误

@servercore.route('/apis/ListServer')
def ListServer():
    template = {
        "errcode": 0,
        "msg": "获取成功",
        "data": []
    }
    if not class_auth.isAuth(request.args.get("token")):
        template["errcode"] = 1
        template["msg"] = "token错误"
    else:
        data = []
        for i in dbc.keys():
            temp = dbc.hgetall(i)
            arr = {}
            for j in temp.keys():
                arr[j.decode()] = temp[j].decode()
            data.append(arr)
        template["data"] = data
    return json.dumps(template)

# 修改服务器api
# 目前只支持修改备注
# 请求方式 GET
# 请求内容
# token -> 令牌
# hash -> 服务器hash
# name -> 名称
# errcode -> 0 成功
# errcode -> 1 token错误
# errocde -> 2 信息不全
# errocde -> 3 服务器不存在

@servercore.route('/apis/EditServer')
def EditServer():
    template = {
        "errcode": 0,
        "msg": "修改成功",
    }
    if not class_auth.isAuth(request.args.get("token")):
        template["errcode"] = 1
        template["msg"] = "token错误"

    else:
        name = request.args.get("name")
        serverid = request.args.get("serverid")
        if name == "" or serverid == "":
            template["errcode"] = 2
            template["msg"] = "信息不全"
        else:
            if dbc.hget(serverid,"serverid") == None:
                template["errcode"] = 3
                template["msg"] = "服务器不存在"
            else:
                dbc.hset(serverid, "name", name)
    return json.dumps(template)