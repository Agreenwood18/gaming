import asyncio


class MyGlobals:
    def __init__(self):
        self.router_loop: asyncio.AbstractEventLoop = 0

myglobals = MyGlobals()
