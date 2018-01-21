class Parser:
    def __init__(self, file):
        self.funcs = {}
        self.file = file

    def route(self, alias:str):
        def decorate(func):
            def fuck(*args, **kwargs):
                return func(*args, **kwargs)
            if alias != "":
                self.funcs[alias] = func
            return fuck
        return decorate
