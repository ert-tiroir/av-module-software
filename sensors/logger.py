
DEBUG   = 0
INFO    = 1
SUCCESS = 2
WARNING = 3
ERROR   = 4

class ModuleLogger:
    def __init__(self, target):
        self.target = target

    def print(self, level, *args):
        S = chr(level) + " ".join(map(lambda x: str(x), args))
        F = bytes(S, encoding = "utf-8")

        self.target.write_string_logger(F)
