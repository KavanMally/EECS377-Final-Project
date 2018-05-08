import paho.mqtt.client as mqtt
from time import sleep

# for raspberry pi
class MosquittoBroker():

    def __init__(self):
        self.client = mqtt.Client(client_id="ec2_id", protocol=paho.mqtt.client.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def serve(self):
        self.client.connect('localhost', 1883, keepalive=60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, rc, unknown):
        self.client.publish(client, 
