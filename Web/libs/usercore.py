# usercore.py
# Author:Lengyue
# manage users

from flask import Blueprint, render_template, abort,url_for, request
import redis
import classes.class_config
import logging
import json
import random
import string
import time

usercore = Blueprint('usercore', __name__,
                        template_folder='templates')

config = classes.class_config.config().read("usercore")
global_config = classes.class_config.config().read("global")
logger = logging.getLogger(config["log"]["name"])
dbc = redis.Redis(db=5, host= global_config["db"]["redis"]["ip"], port= global_config["db"]["redis"]["port"], password= global_config["db"]["redis"]["password"])

# 登录api
# 请求方式 GET
# 请求内容
# password -> 密码
# errcode -> 0 成功
# errcode -> 1 信息不能为空
# errcode -> 2 密码错误
# errcode -> 3 尚未初始化

@usercore.route('/apis/Login')
def Login():
    template = {
        "errcode": 0,
        "msg": "登陆成功",
        "token": ""
    }

    password = request.args.get("password", "")

    if password == "":
        template["errcode"] = 1
        template["msg"] = "信息不能为空"
        return json.dumps(template)

    token = ''.join(random.sample(string.ascii_letters + string.digits, 20))
    ctime = time.time()
    server_password = dbc.hget("user", "password")
    if server_password == None:
        template["errcode"] = 3
        template["msg"] = "我觉得你得先初始化"
    else:
        server_password = server_password.decode()
        if server_password != password:
            template["errcode"] = 2
            template["msg"] = "密码错误"
        else:
            dbc.hset("user", "token", token)
            dbc.hset("user", "last_login", str(ctime))
            template["token"] = token
    return json.dumps(template)


# 初始化密码api
# 请求方式 GET
# 请求内容
# password -> 密码
# errcode -> 0 成功
# errcode -> 1 信息不能为空
# errcode -> 2 密码错误

@usercore.route('/apis/Init')
def Init():
    template = {
        "errcode": 0,
        "msg": "初始化成功",
        "token":""
    }

    password = request.args.get("password", "")

    if password == "":
        template["errcode"] = 1
        template["msg"] = "信息不能为空"
        return json.dumps(template)

    token = ''.join(random.sample(string.ascii_letters + string.digits, 20))
    ctime = time.time()
    server_password = dbc.hget("user", "password")

    if server_password != None:
        template["errcode"] = 2
        template["msg"] = "我觉得不能Init,因为你已经初始化了"
    else:
        dbc.hset("user", "token", token)
        dbc.hset("user", "password", password)
        dbc.hset("user", "last_login", str(ctime))
        template["token"] = token
    return json.dumps(template)

