# Usercore.py
# Author:Lengyue
# manage users

from flask import Blueprint, render_template, abort,url_for, request
import classes.class_MongoDB
import classes.class_config
import logging
import json
import random
import string
import time

usercore = Blueprint('usercore', __name__,
                        template_folder='templates')

config = classes.class_config.config().read("usercore")
logger = logging.getLogger(config["log"]["name"])
dbc = classes.class_MongoDB.MongoClient(config["db"]["mongo"]["uri"], logger, "SYS")

# 登录api
# 请求方式 GET
# 请求内容
# username -> 用户名
# password -> 密码hash
# errcode -> 0 成功
# errcode -> 1 信息不能为空
# errcode -> 2 用户名/密码错误

@usercore.route('/apis/Login')
def Login():
    template = {
        "errcode": 0,
        "msg": "登陆成功",
        "data": {}
    }

    username = request.args.get("username", "")
    password = request.args.get("password", "")

    if username == "" or password == "":
        template["errcode"] = 1
        template["msg"] = "信息不能为空"
        return json.dumps(template)

    token = ''.join(random.sample(string.ascii_letters + string.digits, 20))
    ctime = time.time()
    dbc.update("users", {"username": username, "password": password}, {'last_login': ctime, 'token': token})
    user = dbc.get_one("users",{"username":username,"password":password})

    if user == None:
        template["errcode"] = 2
        template["msg"] = "用户名/密码错误"
        return json.dumps(template)

    user.pop("_id")
    template["data"] = user
    return json.dumps(template)

#更新用户数据
@usercore.route('/apis/UpdateUserInfo')
def UpdateUserInfo():
    template = {
        "errcode": 0,
        "msg": "提交成功",
        "data": {}
    }

    username = request.args.get('username',"")
    update_info = request.args.get('update_info',"")
    token = request.args.get('token', "")
    token_info = dbc.get_one('users',{'token':token})

    if username == "" or update_info == "" or token == "":
        template["errcode"] = 1
        template["msg"] = "信息不全"
        return json.dumps(template)

    if token_info == None:
        template["errcode"] = 2
        template["msg"] = "token错误"
        return json.dumps(template)

    if "user_manager" in token_info["group"] or "admin" in token_info["group"] or token_info["username"] == username:
        dbc.update('users',{'username':username},json.loads(update_info))
        data = dbc.get_one('users',{'username':username})
        data.pop("_id")
        template["data"] = data
    else:
        template["errcode"] = 3
        template["msg"] = "操作无权限"

    return json.dumps(template)
