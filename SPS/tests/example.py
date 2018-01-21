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