import json

class config:
    def read(self, filename):
        return json.loads(open("./configs/%s.json" % filename, "r", encoding="utf-8").read())