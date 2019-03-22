import uuid
import socket


class Message:
    def reg(self):
        """注册信息"""
        return {
            "type":'register',
            "payload":{
                "id":uuid.uuid4().hex,#唯一的id
                "hostname":socket.gethostname(),#获取主机名
                "ip":[]
            }
        }


