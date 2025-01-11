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
        self._client_id = None
        self._ca_certs = None
        self._certfile = None
        self._key_file = None
        self.client.on_connect = self._on_connect
        self.msg = []
        # TODO 证书秘钥等从哪里获取暂时没有定

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.disconnect()

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

    @property
    def certfile(self):
        """
        证书
        :return:
        """
        return self._certfile

    @certfile.setter
    def certfile(self, value: str):
        """
        :param: value:str
        :return:
        """
        self._certfile = value

    @property
    def key_file(self):
        """
        秘钥文件
        :return:
        """
        return self._key_file

    @key_file.setter
    def key_file(self, value: str):
        """
        :param value:
        :return:
        """
        self._key_file = value

    @property
    def client_id(self):
        """
        客户端ID
        :return:
        """
        return self._client_id

    @client_id.setter
    def client_id(self, value: str):
        """
        :param value:
        :return:
        """
        self._client_id = value

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


class MQTTPublisher(MQTTBase):
    """发布类"""

    def __init__(self, env=None, broker=None, port=None, topic=None, msg=None):
        self.topic = topic
        super().__init__(env, broker, port, topic)

    def _on_message(self):
        """接受消息的回调函数"""
        print(f"接收到消息：{self.topic.payload.decode()}")

    def publish(self, payload=None, qos=0, retain=False, interval=1):
        """
        发布消息
        :param interval: 发布消息间隔
        :param payload: 消息内容
        :param qos: 服务质量
        :param retain: 保留
        :return:
        """
        if not self.client:
            self.connect()
        try:
            self.client.publish(self.topic, payload, qos=qos, retain=retain)
            self.client.loop_forever()
        except Exception as e:
            print(f"发布消息出错了：{e}")
        finally:
            self.client.disconnect()


class MQTTSubscriber(MQTTBase):
    """订阅类"""

    def __init__(self, env=None, broker=None, port=None, topic=None):
        super().__init__(env, broker, port, topic)
        self.topic = topic

    def _on_message(self):
        """
        消息接收回调函数
        :return:
        """
        decode_msg = self.topic.payload.decode()
        print(f"接收到消息：{decode_msg}")


    @property
    def message(self):
        """
        获取消息
        :return:
        """
        return self.msg

    def subscribe(self, qos=0):
        """
        订阅消息
        :param qos: 服务质量
        :return:
        """
        if not self.client:
            self.connect()
        try:
            self.client.subscribe(self.topic, qos)
            self.client.on_message = self._on_message
            self.client.loop_start()
            self.client.loop_forever(timeout=10)
        except Exception as e:
            print(f"订阅消息出错了：{e}")
        finally:
            self.disconnect()

    def unsubscribe(self, topic):
        """取消订阅"""
        self.client.unsubscribe(topic)
        print(f"Unsubscribed from {topic}")

    def disconnect(self):
        """断开 MQTT 服务器连接"""
        # 停止线程
        self.client.loop_stop()
        print("Stopped the network loop by MQTTSubscriber")
        # 断开连接
        self.client.disconnect()
        print("Disconnected from MQTT broker by MQTTSubscriber")
