# from subprocess import Popen,PIPE
#
# proc = Popen('echo "hello"',shell=True,stdout=PIPE,stderr=PIPE) #shell表示使用shell执行rags
# code = proc.wait()
# txt = proc.stdout.read()  #PIPE管道就能获取标准输出，不然就是None
# # txt = proc.stderr.read() #标准错误，获取同上
# print(code,txt)

# import zerorpc
# import threading
#
# client = zerorpc.Client()
# client.connect('tcp://127.0.0.1:9000')
# e = threading.Event()
# while True:
#     print(client.hello(__name__))  # 获取到的返回信息是经过序列化和反序列化的
#     e.wait(3)
#
# client.close()

from agent import Agent

if __name__ == '__main__':
    agent = Agent()
    try:
        agent.start()
    except KeyboardInterrupt as e:
        agent.shutdown()

