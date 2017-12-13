# taskcore.py
# Author:Lengyue
# manage users

from flask import Blueprint, request
import redis
from classes import class_config, class_auth
import logging
import json
import random
import string
import time

taskcore = Blueprint('taskcore', __name__,
                        template_folder='templates')

config = class_config.config().read("taskcore")
global_config = class_config.config().read("global")
logger = logging.getLogger(config["log"]["name"])
dbc = redis.Redis(db=6, host= global_config["db"]["redis"]["ip"], port= global_config["db"]["redis"]["port"], password= global_config["db"]["redis"]["password"])

# 获取爬虫列表api
# 请求方式 GET
# 请求内容
# token -> 令牌
# errcode -> 0 成功
# errcode -> 1 token错误

@taskcore.route('/apis/ListTask')
def ListTask():
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



# 添加/修改爬虫api
# 请求方式 GET
# 请求内容
# token -> 令牌
# name -> 爬虫名字
# parser -> 解析器
# description -> 描述
# page -> web页面地址
# errcode -> 0 成功
# errcode -> 1 token错误
# errocde -> 2 信息不全

@taskcore.route('/apis/EditTask')
def EditTask():
    template = {
        "errcode": 0,
        "msg": "添加/修改成功",
    }
    if not class_auth.isAuth(request.args.get("token")):
        template["errcode"] = 1
        template["msg"] = "token错误"

    else:
        name = request.args.get("name")
        parser = request.args.get("parser")
        description = request.args.get("description")
        page = request.args.get("page")
        if name == "" or parser == "" or description == "" or page == "":
            template["errcode"] = 2
            template["msg"] = "信息不全"
        else:
            dbc.hset(name, "name", name)
            dbc.hset(name, "parser", parser)
            dbc.hset(name, "description", description)
            dbc.hset(name, "page", page)
    return json.dumps(template)

# 删除爬虫api
# 请求方式 GET
# 请求内容
# name -> 爬虫名字
# errcode -> 0 成功
# errcode -> 1 token错误
# errocde -> 2 信息不全

@taskcore.route('/apis/RemoveTask')
def RemoveTask():
    template = {
        "errcode": 0,
        "msg": "删除成功",
    }
    if not class_auth.isAuth(request.args.get("token")):
        template["errcode"] = 1
        template["msg"] = "token错误"

    else:
        name = request.args.get("name")
        if name == "":
            template["errcode"] = 2
            template["msg"] = "信息不全"
        else:
            dbc.delete(name)
    return json.dumps(template)
