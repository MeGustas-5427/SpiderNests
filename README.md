# SpiderNests
SpiderNests - New kind of Spider Engine

Based on Python3 aio uvloop

If you have a redis server listen on 127.0.0.1:6379

You just have to

    git clone https://github.com/SpiderNests/SpiderNests
    pip3 install uvloop //Linux
    cd ./LRS
    python3 setup.py install
    screen python3 run.py -S LRS
    cd ../SPS
    python3 setup.py install
    
  
Then Enjoy it:)

If you want to make it distribute
Please modify the server_id in the config.json to make it unique
Demo for SPS

    from SpiderNestsParseService import SPS
    from SpiderNestsParseService.log import *
    from lxml import etree
    app = SPS()


    @app.main()
    async def start():
        app.requests("http://www.xicidaili.com/", firstpage, headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/63.0.3239.132 Mobile Safari/537.36"
        }, proxy="http://127.0.0.1:8888")

    async def validate(content, args):
        if "text" in content["result"].keys():
            if "zhihu" in content["result"]["text"]:
                logger.info("[Validate Success] Proxy -> " + args["proxy"])
        else:
            logger.info("[Validate Failed] Proxy -> " + args["proxy"])

    async def firstpage(content):
        #print(content["result"]["content"])
        tree = etree.HTML(content["result"]["text"])
        for i in tree.xpath('//tr[@class="odd"]'):
            if i.xpath('td[6]/text()') == ['HTTPS']:
                proxy = "http://" + i.xpath('td[2]/text()')[0] + ":" + i.xpath('td[3]/text()')[0]
                app.requests("http://www.zhihu.com/", validate, headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/63.0.3239.132 Mobile Safari/537.36"
                }, proxy=proxy, args={"proxy": proxy})
                logger.info("Got proxy -> " + proxy)

    app.run(config="./config.json")
    
    config.json ->
    
    {
      "redis":{ // Redis config
        "host":"127.0.0.1",
        "port":6379,
        "password":"",
        "db":0
      },
      "server_id": "320d4ce956e49bbc812b61ecc25f3631" // Server unique id
    }
