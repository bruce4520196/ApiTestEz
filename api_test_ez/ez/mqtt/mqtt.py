# -*- coding:utf-8 -*-
# @FileName  :mqtt.py
# @Time      :2024/12/9 15:11
# @Author    :wangfei

from paho.mqtt import client as mqtt
from api_test_ez.project import Project

class MQTTBase:
    """
    MQTT基类
    """

    def __init__(self, env=None, broker=None, port=None, topic=None):
        self.env = env
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.client_id = None
        self._ca_certs = None
        self.key_file = None
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        project = Project()


    @classmethod
    def _on_connect(cls, client, userdata, flags, rc, properties=None):
        """
        连接后回调函数，会在MQTT客户端连接成功后被调用
        :return:
        """
        rc_status = {
            0: "连接成功",
            1: "协议版本不正确",
            2: "客户端标识符无效",
            3: "服务器不可用",
            4: "用户名或密码不正确",
            5: "未经授权",
        }
        print(f"Connect by MQTTPublisher->{rc_status.get(int(rc))}->Code:{rc}")

    @property
    def ca_certs(self):
        """
        根证书
        :return:
        """
        return self._ca_certs

    @ca_certs.setter
    def ca_certs(self, value: str):
        """
        :param: value:str
        :return:
        """
        self._ca_certs = value

    def _on_message(self):
        """
        获取MQTT消息
        :return:
        """
        pass

    def connect(self) -> mqtt.Client:
        """
        连接MQTT服务器
        :return:
        """
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.tls_set(
            ca_certs=self.ca_certs
        )

        return self.client
