#-*- encoding: UTF-8 -*-
from setuptools import setup

setup(
    name = "LRS",          # 包名
    version = "0.1",              # 版本信息
    packages = ['LengyueRequestsService'],  # 要打包的项目文件夹
    include_package_data=True,    # 自动打包文件夹内所有数据
    zip_safe=True,                # 设定项目包为安全，不用每次都检测其安全性

    install_requires = [          # 安装依赖的其他包
        "aiohttp==2.3.9",
        "aioredis==1.0.0",
        "async-timeout==2.0.0",
        "chardet==3.0.4",
        "hiredis==0.2.0",
        "idna==2.6",
        "json5==0.6.0",
        "multidict==4.0.0",
        "psutil==5.4.3",
        "yarl==1.0.0",

    ],

    # 设置程序的入口为hello
    # 安装后，命令行执行hello相当于调用hello.py中的main方法
    #entry_points={
    #    'console_scripts':[
    #        'hello = project_file.hello:main'
    #    ]
    # },

    # 如果要上传到PyPI，则添加以下信息
    # author = "Me",
    # author_email = "me@example.com",
    # description = "This is an Example Package",
    # license = "MIT",
    # keywords = "hello world example examples",
    # url = "http://example.com/HelloWorld/",   
 )