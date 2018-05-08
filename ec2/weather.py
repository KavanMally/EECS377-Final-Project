#!/usr/bin/python

import pyowm
from paho.mqtt.client import Client
from time import sleep


mqtt = Client()
mqtt.connect("localhost", 50001, 60)
sleep(.3)

k = "2d19784349d26a0853b4c54397d7ff07"
owm =  pyowm.OWM(k)
observation = owm.weather_at_place('Cleveland, US')
w = observation.get_weather()

temperature = w.get_temperature('fahrenheit')['temp_min']
print "looks like it's going to get down to {} ".format(temperature)
mqtt.publish("/devices/b827eb679fe8/sparti/weather/temperature", payload=temperature)
sleep(.3)

if temperature < 50:
    print "It is going to be cold!"
    mqtt.publish("/devices/b827eb679fe8/sparti/weather/cold", payload="1")
    sleep(.3)


else:
    print "It's going to be warm"
    mqtt.publish("/devices/b827eb679fe8/sparti/weather/cold", payload="0")
    sleep(.3)


if w.get_clouds() > 50: 
    print "It's going to be cloudy!"
if not w.get_rain() or 0 in  w.get_rain(): 
    print "It's not going to rain today!"
    mqtt.publish("/devices/b827eb679fe8/sparti/weather/rain", payload="0")
    sleep(.3)


else: 
    print "Grab your umbrella!", w.get_rain()
    mqtt.publish("/devices/b827eb679fe8/sparti/weather/rain", payload="1")
    sleep(.3)


if w.get_snow(): 
    print "Grab your snow boots too!"
    mqtt.publish("/devices/b827eb679fe8/sparti/weather/snow", payload="1")
    sleep(.3)


else:
    print "Looks like there's no snow!"
    mqtt.publish("/devices/b827eb679fe8/sparti/weather/snow", payload="0")
    sleep(.3)

