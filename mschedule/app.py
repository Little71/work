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

import ipaddress
ip = ipaddress.ip_address('127.0.0.1')

import netifaces
ifaces = netifaces.interfaces() #获取当前主机名
for iface in ifaces:
    ips = netifaces.ifaddresses(iface)
    #获取主机名的地址信息
    if 2 in ips :
        for ip in ips[2]:
            print(ip['addr'])
