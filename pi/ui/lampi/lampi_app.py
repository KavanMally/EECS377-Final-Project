from kivy.app import App
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from math import fabs
import json
import os
from paho.mqtt.client import Client
import pigpio
import lampi_util
from lamp_common import *
import pyowm
from time import sleep

MQTT_CLIENT_ID = "lamp_ui"


PROJECT_ID = 'FILL_IN'
WRITE_KEY = 'FILL_IN'

version_path = os.path.join(os.path.dirname(__file__), '__VERSION__')
try:
    with open(version_path, 'r') as version_file:
        LAMPI_APP_VERSION = version_file.read()
except IOError:
    # if version file cannot be opened, we'll stick with unknown
    LAMPI_APP_VERSION = 'Unknown'


class LampiApp(App):
    _updated = False
    _updatingUI = False
    _hue = NumericProperty()
    _saturation = NumericProperty()
    _brightness = NumericProperty()
    lamp_is_on = BooleanProperty()

    temperature = NumericProperty(0)
    rain = BooleanProperty(False)
    snow = BooleanProperty(False)


    def _get_hue(self):
        return self._hue

    def _set_hue(self, value):
        self._hue = value

    def _get_saturation(self):
        return self._saturation

    def _set_saturation(self, value):
        self._saturation = value

    def _get_brightness(self):
        return self._brightness

    def _set_brightness(self, value):
        self._brightness = value

    hue = AliasProperty(_get_hue, _set_hue, bind=['_hue'])
    saturation = AliasProperty(_get_saturation, _set_saturation,
                               bind=['_saturation'])
    brightness = AliasProperty(_get_brightness, _set_brightness,
                               bind=['_brightness'])
    gpio17_pressed = BooleanProperty(False)
    device_associated = BooleanProperty(True)


    def _update_temperature(self):
        pass 

    def on_start(self):
        self._publish_clock = None
        self.mqtt_broker_bridged = False
        self._associated = True
        self.association_code = None
        self.mqtt = Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.will_set(client_state_topic(MQTT_CLIENT_ID), "0",
                           qos=2, retain=True)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()
        self.set_up_GPIO_and_device_status_popup()
        self.associated_status_popup = self._build_associated_status_popup()
        self.associated_status_popup.bind(on_open=self.update_popup_associated)

        k = "2d19784349d26a0853b4c54397d7ff07"
        owm =  pyowm.OWM(k)
        observation = owm.weather_at_place('Cleveland, US')
        w = observation.get_weather()
        self.temperature = w.get_temperature('fahrenheit')['temp_min']

        if w.get_rain() > 50:
            self.rain = True
        else:
            self.rain = False

        if w.get_snow():
            self.snow = True
        else:
            self.snow = False

        Clock.schedule_interval(self._poll_associated, 0.1)
        #lbl = Label(text="test")
        #Clock.schedule_once(lambda dt: self.show_marks(lbl), 1)
        #self.add_widget(lbl)
        #self.ids['temperature'].text='test1'
        #self.temperature = ObjectProperty(None)
        #self.temperature.text = "test"

    def _build_associated_status_popup(self):
        return Popup(title='Associate your Lamp',
                     content=Label(text='Msg here', font_size='30sp'),
                     size_hint=(1, 1), auto_dismiss=False)

    def on_hue(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_saturation(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_brightness(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def on_lamp_is_on(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_leds(), 0.01)

    def _create_event_record(self, element, value):
        return {'element': {'id': element, 'value': value}}

    def on_connect(self, client, userdata, flags, rc):
        self.mqtt.publish(client_state_topic(MQTT_CLIENT_ID), "1",
                          qos=2, retain=True)
        self.mqtt.message_callback_add(TOPIC_LAMP_CHANGE_NOTIFICATION,
                                       self.receive_new_lamp_state)
        self.mqtt.message_callback_add(broker_bridge_connection_topic(),
                                       self.receive_bridge_connection_status)
        self.mqtt.message_callback_add(TOPIC_LAMP_ASSOCIATED,
                                       self.receive_associated)
        self.mqtt.subscribe(broker_bridge_connection_topic(), qos=1)
        self.mqtt.subscribe(TOPIC_LAMP_CHANGE_NOTIFICATION, qos=1)
        self.mqtt.subscribe(TOPIC_LAMP_ASSOCIATED, qos=2)
        #self.RelativeLayout.ids.temperature.text = "test"
        print("test")
        #print(self.__dict__.keys())
        #print(self.root.ids.temperature.text)
        
    def on_message(self, client, userdata, msg):
        #temperature reading
        if "temperature" in msg.topic:
            temperature = msg.payload
        #is raining
        elif "rain" in msg.topic:
            if msg.payload == "1":
                pass
            else:
                pass
        #is cold
        elif "cold" in msg.topic:
            if msg.payload == "1":
                pass
            else:
                pass
        #is snowing
        elif "snow" in msg.topic:
            if msg.payload == "1":
                pass
            else:
                pass
    def _poll_associated(self, dt):
        # this polling loop allows us to synchronize changes from the
        #  MQTT callbacks (which happen in a different thread) to the
        #  Kivy UI
        self.device_associated = self._associated

    def receive_associated(self, client, userdata, message):
        # this is called in MQTT event loop thread
        new_associated = json.loads(message.payload)
        if self._associated != new_associated['associated']:
            if not new_associated['associated']:
                self.association_code = new_associated['code']
            else:
                self.association_code = None
            self._associated = new_associated['associated']

    def on_device_associated(self, instance, value):
        if value:
            self.associated_status_popup.dismiss()
        else:
            self.associated_status_popup.open()

    def update_popup_associated(self, instance):
        code = self.association_code[0:6]
        instance.content.text = ("Please use the\n"
                                 "following code\n"
                                 "to associate\n"
                                 "your device\n"
                                 "on the Web\n{}".format(code)
                                 )

    def receive_bridge_connection_status(self, client, userdata, message):
        # monitor if the MQTT bridge to our cloud broker is up
        if message.payload == "1":
            self.mqtt_broker_bridged = True
        else:
            self.mqtt_broker_bridged = False

    def receive_new_lamp_state(self, client, userdata, message):
        new_state = json.loads(message.payload)
        Clock.schedule_once(lambda dt: self._update_ui(new_state), 0.01)

    def _update_ui(self, new_state):
        if self._updated and new_state['client'] == MQTT_CLIENT_ID:
            # ignore updates generated by this client, except the first to
            #   make sure the UI is syncrhonized with the lamp_service
            return
        self._updatingUI = True
        try:
            if 'color' in new_state:
                    self.hue = new_state['color']['h']
                    self.saturation = new_state['color']['s']
            if 'brightness' in new_state:
                self.brightness = new_state['brightness']
            if 'on' in new_state:
                self.lamp_is_on = new_state['on']
        finally:
            self._updatingUI = False

        self._updated = True

    def _update_leds(self):
        msg = {'color': {'h': self._hue, 's': self._saturation},
               'brightness': self._brightness,
               'on': self.lamp_is_on,
               'client': MQTT_CLIENT_ID}
        self.mqtt.publish(TOPIC_SET_LAMP_CONFIG, json.dumps(msg), qos=1)
        self._publish_clock = None

    def set_up_GPIO_and_device_status_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.network_status_popup = self._build_network_status_popup()
        self.network_status_popup.bind(on_open=self.update_device_status_popup)

    def _build_network_status_popup(self):
        return Popup(title='Device Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_device_status_popup(self, instance):
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        deviceid = lampi_util.get_device_id()
        msg = ("Version: {}\n"
               "{}: {}\n"
               "DeviceID: {}\n"
               "Broker Bridged: {}\n"
               "threaded"
               ).format(
                        LAMPI_APP_VERSION,
                        interface,
                        ipaddr,
                        deviceid,
                        self.mqtt_broker_bridged)
        instance.content.text = msg

    def on_gpio17_pressed(self, instance, value):
        if value:
            self.network_status_popup.open()
        else:
            self.network_status_popup.dismiss()

    def _poll_GPIO(self, dt):
        # GPIO17 is the rightmost button when looking front of LAMPI
        self.gpio17_pressed = not self.pi.read(17)
