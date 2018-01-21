from ParserService.bind import Parser

test = Parser(__file__)

@test.route("fuck")
def fuck(text: str):
    # do something
    print(text)
