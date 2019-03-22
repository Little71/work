import threading

import zerorpc

from .config import CONNECTION_URL
from util import getlogger

logger = getlogger(__name__,'x:/xxx')

class ConnectionManager:
    def __init__(self):
        self.client = zerorpc.Client()
        self.event = threading.Event()

    def start(self,timeout=None):
        '''建立连接'''
        self.client.connect(CONNECTION_URL)

        while not self.event.wait(timeout):
            pass

    def shutdown(self):
        self.event.set()
        self.client.close()












