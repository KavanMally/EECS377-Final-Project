#!/usr/bin/env python

from paho.mqtt.client import Client
from time import sleep
import json

#bus_routine = False
blinking = False
status = True

shuttles = False

def on_connect(mqttc, obj, flags, rc):
    print("rc:" + str(rc))

def on_message(mqttc, obj, message):

    #global bus_routine
    global shuttles

    print("received message")
    if "awoken" in message.payload:
        print("user awoken")
        # start bus lighting routine based on message
        shuttles = True
    if "Arriving In" in message.payload and shuttles:

        print("received bus schedule payload")
        #if bus_routine == False:
        #bus_routine = True
        data = json.loads(message.payload)
        run_bus_routine(data, mqttc)


def on_publish(mqttc, obj, mid):
    print("on publish")

def run_bus_routine(message, mqttc):

    global blinking

    # hardcode test data
    data = message["Bellflower & Ford"][0]
    print(data)

    parse = data.split(" ")
    #minutes = int(parse[2])
    #seconds = int(parse[5])

    # debug purposes
    minutes = int(parse[5])
    seconds = int(parse[2])
    
    print("minutes: " + str(minutes))


    #hue = minutes / 120.0 # set hue to this value
    hue = 1
    # saturation = 1
    saturation = (100 - (100 * minutes / 60.0))/100.0
    print("saturation: " + str(saturation))
    brightness = 1

    #mqtt = Client()
    #mqtt.on_message = on_message
    #mqtt.on_connect = on_connect
    #mqtt.connect("localhost", 1883, 60)
    #sleep(0.5)
    #global mqtt


    if minutes > 0:
        # publish
        msg = getMessage(hue, saturation, brightness)
        mqttc.publish("/lamp/set_config", payload=json.dumps(msg), qos=1, retain=True)

    # blinking
    if minutes < 1 and seconds > 0:
        if not blinking:
            blinking = True
            #blink_lights()

    #else:
    #    global bus_routine
    #    bus_routine = False


def blink_lights():
    global blinking
 
    print("blinking")

    #mqtt = Client()
    #mqtt.on_message = on_message
    #mqtt.on_connect = on_connect
    #mqtt.connect("localhost", 1883, 60)
    #sleep(0.5)
    #global mqtt

    counter = 0

    # 60 second cycle
    while blinking:
        mqtt.publish("/lamp/set_config", payload=json.dumps(on_off()), qos=1)
        sleep(5)

        if counter == 12:
            blinking = False
        else:
            counter = counter + 1




def getMessage(hue, saturation, brightness):
       
    msg = {'color': {'h': hue, 's': saturation},
              'brightness': brightness, 
              'on': True, 
              'client': "pi"}
    return msg

def on_off():

    global status

    msg = {'color': {'h': 1, 's': 0},
              'brightness': 1, 
              'on': status, 
              'client': "pi"}
    
    status = not status
    return msg



mqtt = Client()
mqtt.on_message = on_message
mqtt.on_connect = on_connect
mqtt.on_publish = on_publish

mqtt.connect("localhost", 1883, 3600)

sleep(0.5)

mqtt.subscribe("/sparti/transport/bus_schedule", 0)
mqtt.subscribe("/sparti/android/sleep", 0)


sleep(0.5)

mqtt.loop_forever()

