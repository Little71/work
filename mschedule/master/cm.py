from agent.config import PATH_LOG
from master.storage import Storage
from util import getlogger

logger = getlogger(__name__,PATH_LOG)

class ConnectionManager:
    def __init__(self):
        self.store = Storage()

    def handle(self, msg):
        try:
            print(msg, type(msg))
            if msg['type'] in {'register', 'heartbeat'}:
                self.store.reg_hb(**msg['payload'])
            elif msg['type'] == "result":
                self.store.result(**msg['payload'])

            print(self.store.get_agents())
            return f'ack {msg}'
        except Exception as e:
            logger.error(f'Error:{e}')

    sendmsg = handle

    def add_task(self,msg):
        return self.store.add_task(msg)

    def get_task(self,agent_id):
        return self.store.get_task(agent_id)

    def get_agents(self):
        return self.store.get_agents()


