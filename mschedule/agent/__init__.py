from agent.cm import ConnectionManager
import threading



class Agent:
    def __init__(self):
        self.event = threading.Event()
        self.cm = ConnectionManager()

    def start(self):
        while not self.event.is_set():
            try:
                self.cm.start()
                # threading.Thread(target=cm.start).start()
                # 不要把zerorpc实现的方法放到线程中去，会抛异常
                # cm.join()
            except Exception as e:
                self.cm.shutdown()
            self.event.wait(3)

    def shutdown(self):
        self.event.set()
        self.cm.shutdown()