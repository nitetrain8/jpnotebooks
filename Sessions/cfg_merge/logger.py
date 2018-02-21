

class Logger():
    def __init__(self, fn=None, lvl=1):
        self.fn = fn
        if self.fn:
            self.f = open(fn, 'w')
        else:
            self.f = None
        self.lvl = lvl
        self.to_console = True

    def print1(self, s, lvl, *args, **kw):
        if lvl > self.lvl:
            return
        if self.to_console:
            print(s, *args, **kw)
        if self.f is not None:
            print(s, *args, **kw, file=self.f)

    def close(self):
        if self.f is not None:
            self.f.close()


_G_LOGGER = None

def open_log(fn=None, lvl=1):
    global _G_LOGGER
    close_log()
    _G_LOGGER = Logger(fn, lvl)

def close_log():
    global _G_LOGGER
    if _G_LOGGER is not None:
        _G_LOGGER.close()

def log(s, lvl, *a, **kw):
    global _G_LOGGER
    if _G_LOGGER is not None:
        _G_LOGGER.print1(s, lvl, *a,**kw)

def log1(s, *a,**kw):
    log(s, 1, *a, **kw)

def log2(s, *a, **kw):
    log(s, 2, *a, **kw)
