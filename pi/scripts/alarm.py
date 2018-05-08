#!/usr/bin/env python

from paho.mqtt.client import Client
from time import sleep
import json

def on_connect(mqttc, obj, flags, rc):
    print("rc:" + str(rc))



def on_message(mqttc, obj, message):

    # turn red when user snoozes android alarm
    if "awoken" in message.payload:
        print("user has woken")
	print(str(message.payload))

        msg = {'color': {'h': 1, 's': 1},
               'brightness': 1,
               'on': True,
               'client': "android"}

        mqttc.publish("/lamp/set_config", payload=json.dumps(msg), qos=1, retain=True)


def on_publish(mqttc, obj, mid):
    print("on publish")

def on_subscribe(mqttc, obj, mid, granted_qos):
    pass

def on_log(mqttc, obj, level, string):
    print(string)


mqttc = Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.connect("localhost", 1883, 60)

sleep(0.5)

mqttc.subscribe("/sparti/android/sleep", 0)

sleep(0.5)

mqttc.loop_forever()
