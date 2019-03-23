import threading

import zerorpc

from agent.msg import Message
from .config import CONNECTION_URL, TIMEOUT
from util import getlogger

logger = getlogger(__name__, 'x:/xxx')


class ConnectionManager:
    def __init__(self):
        self.client = zerorpc.Client()
        self.event = threading.Event()
        self.message = Message('x:/xxx')

    def start(self, timeout=TIMEOUT):
        '''建立连接'''
        try:
            self.event.clear()#重连时候清除event信息
            self.client.connect(CONNECTION_URL)
            self.client.sendmsg(self.message.reg())

            while not self.event.wait(timeout):
                self.client.sendmsg(self.message.heartbeat())
        except Exception as e:
            logger.error(f'Error {e}')
            raise e

    def shutdown(self):
        self.event.set()
        self.client.close()

    # def join(self):
    #     self.event.wait()
