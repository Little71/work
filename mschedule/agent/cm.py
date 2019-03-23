import threading

import zerorpc

from agent.executor import Executor
from agent.msg import Message
from .config import CONNECTION_URL, TIMEOUT
from util import getlogger
from .state import *

logger = getlogger(__name__, 'x:/xxx')


class ConnectionManager:
    def __init__(self):
        self.client = zerorpc.Client()
        self.event = threading.Event()
        self.message = Message('x:/xxx')
        self.state = WAITING  # 任务状态
        self.exec = Executor()

    def start(self, timeout=TIMEOUT):
        '''建立连接'''
        try:
            self.event.clear()  # 重连时候清除event信息
            self.client.connect(CONNECTION_URL)
            logger.info(self.client.sendmsg(self.message.reg()))

            while not self.event.wait(timeout):
                logger.info(self.client.sendmsg(self.message.heartbeat()))
                # if self.state in (SUCCESS,FAILED):
                #     self.client.sendmsg(self.message.result())
                #     self.state = WAITING
                #主动去领取任务
                if self.state == WAITING:
                    task = self.client.get_task(self.message.id)
                    if task:
                        self.state = RUNNING
                        code,ouput = self.exec.run(task[1],task[2])
                        # 这的阻塞执行不知道要执行多久，所以可以用异步
                        # 这里可以开启一个线程去异步执行任务，但是不能保证下面马上获取到信息然后返回
                        # 所以可以在上面做判断是否属于工作状态或者完成任务了，然后就去获取信息发送

                        # if code == 0:
                        #     self.state = SUCCESS
                        # else:
                        #     self.state = FAILED
                        self.client.sendmsg(self.message.result(task[0],code,ouput))
                        self.state = WAITING

        except Exception as e:
            logger.error(f'Error {e}')
            raise e

    def shutdown(self):
        self.event.set()
        self.client.close()

    # def join(self):
    #     self.event.wait()
