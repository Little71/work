import zerorpc

MASTER_URL = "tcp://0.0.0.0:9000"
class Master:
    def hello(self,msg):
        return f'ack.hello{msg}'

server =zerorpc.Server(Master())
server.bind(MASTER_URL)
server.run()

print('~~~~~~~~~~')