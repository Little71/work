import uuid
import socket
import os
import ipaddress

import netifaces


class Message:
    def __init__(self, myidpath):
        if os.path.exists(myidpath):
            with open(myidpath) as f:
                self.id = f.readline().strip()
        else:
            self.id = uuid.uuid4().hex
            with open(myidpath, 'w') as f:
                f.write(self.id)

    def reg(self):
        """注册信息"""
        return {
            "type": 'register',
            "payload": {
                "id": self.id,  # 唯一的id
                "hostname": socket.gethostname(),  # 获取主机名
                "ip": self._get_addresses()
            }
        }

    @staticmethod
    def _get_addresses():
        addresses = []
        for iface in netifaces.interfaces():  # 获取当前主机名
            ips = netifaces.ifaddresses(iface)
            # 获取主机名的地址信息
            if 2 in ips:
                for ip in ips[2]:
                    address = ipaddress.ip_address(ip['addr'])
                    if address.is_loopback or address.is_reserved or \
                            address.is_multicast or address.is_link_local:
                        continue
                    addresses.append(str(address))
        return addresses

    def heartbeat(self):
        """心跳信息"""
        return {
            "type": 'heartbeat',
            "payload": {
                "id": self.id,  # 唯一的id
                "hostname": socket.gethostname(),  # 获取主机名
                "ip": self._get_addresses()
            }
        }

    def result(self,task_id,code,ouput):
        """心跳信息"""
        return {
            "type": "result",
            "payload": {
                "id": task_id,
                "agent_id": self.id,
                "code": code,
                "putput": ouput
            }
        }
