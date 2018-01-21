#-*- encoding: UTF-8 -*-
from setuptools import setup

setup(
    name = "SpiderNests_SPS",
    version = "0.1",
    packages = ['SpiderNestsParseService'],
    include_package_data=True,
    zip_safe=True,

    install_requires = [
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
 )