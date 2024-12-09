# -*- coding:utf-8 -*-
# @FileName  :mqtt.py
# @Time      :2024/12/9 15:11
# @Author    :wangfei

from paho.mqtt import client as mqtt

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
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message


