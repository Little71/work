import datetime
import uuid

from .task import Task
from .state import *


class Storage:
    def __init__(self):
        self.agents = {}
        self.tasks = {}

    def reg_hb(self, **payload):
        agent = self.agents['id']
        agent['timestamp'] = datetime.datetime.now().timestamp()
        agent['busy'] = False  # anget忙不忙，即有没有任务
        agent['info'] = payload

        # self.agents[payload['id']] = Agent(**payload)
        # 每次发心跳包都会创建一个新的对象，频繁激活gc太耗费资源

    def get_agents(self):
        return list(self.agents.keys())

    def add_task(self, msg: dict):
        msg['task_id'] = uuid.uuid4().hex
        task = Task(**msg)
        self.tasks[task.id] = task
        return task.id

        # {
        #     "task":t.id,
        #     "script":t.script,
        #     "timeout":t.timeout,
        #     "parallel":t.parallel,
        #     "fail_rate":t.fail_rate,
        #     "fail_count":t.fail_count,
        #     "state":t.state,
        #     "targets":t.targets,
        # }

    def iter_task(self,state=(WAITING,RUNNING)):
        yield from (task for task in self.tasks.values() if task.state in state)

    # filter(lambda task: task.state in (WAITING, RUNNING), self.tasks.values())

    def get_task(self, agent_id):
        for task in self.iter_task():
            if agent_id in task.targets:
                if task.state == WAITING:
                    task.state = RUNNING
                task.targets[agent_id]['state'] = RUNNING
                return [task.id,task.script,task.timeout]


    def result(self,msg:dict):
        task = self.tasks[msg['id']]
        #要执行完就去改变 self.state ?
        agent = task.targets[msg['agent_id']]
        if msg['code'] == 0:
            agent['state'] = SUCCESS
        else:
            agent['state'] = FAILED

