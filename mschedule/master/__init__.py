import zerorpc

from .cm import ConnectionManager
from .config import MASTER_URL


class Master:
    def __int__(self):
        self.server = zerorpc.Server(ConnectionManager())

    def start(self):
        self.server.bind(MASTER_URL)
        self.server.run()

    def shutdown(self):
        self.server.close()
