class Parser:
    def __init__(self):
        self.funcs = {}

    def route(self, alias:str):
        def decorate(func):
            def fuck(*args, **kwargs):
                return func(*args, **kwargs)
            if alias != "":
                if alias in self.funcs.keys():
                    raise KeyError("alias was existed!")
                self.funcs[alias] = func
            return fuck
        return decorate
