import sys
import time

if sys.platform == "esp8266" or sys.platform == "esp32":
    import network
    import ntptime
    import ubinascii as binascii
    import ujson as json
    import urequests as requests
elif sys.platform == "linux":
    import binascii
    import json
    import requests

VERSION = "linka_mpv0.0.1"


class LinkaSensor:
    def __init__(self, sensor, config):
        self.configure_network(config["ssid"], config["psk"])

        if sys.platform == "esp8266" or sys.platform == "esp32":
            # Configure time
            ntptime.settime()

        self.sensor = sensor
        self.sensor_id = self.get_mac()
        self.api_key = config["api_key"]
        self.description = config["description"]
        self.latitude = config["latitude"]
        self.longitude = config["longitude"]
        self.linka_url = config["linka_url"]
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-api-key": self.api_key,
        }

    @staticmethod
    def get_mac():
        if sys.platform == "esp8266" or sys.platform == "esp32":
            ap_if = network.WLAN(network.AP_IF)
            mac = binascii.hexlify(ap_if.config("mac")).decode()[-6:].upper()
        else:
            import uuid

            mac = str(uuid.getnode())[-6:]
        return mac

    @staticmethod
    def configure_network(ssid, psk):
        if sys.platform == "esp8266" or sys.platform == "esp32":
            sta_if = network.WLAN(network.STA_IF)
            sta_if.active(True)
            sta_if.connect(ssid, psk)
            while not sta_if.isconnected():
                time.sleep(1)
        else:
            pass

    def read_data(self):
        data = None

        pm_data = self.sensor.read()

        if pm_data:
            now = time.gmtime()
            timestamp = f"{now[0]}-{now[1]:02d}-{now[2]:02d}T{now[3]:02d}:{now[4]:02d}:{now[5]:02d}.000Z"

            data = [
                {
                    "sensor": self.sensor.__class__.__name__,
                    "source": self.sensor_id,
                    "version": VERSION,
                    "description": self.description,
                    "pm1dot0": pm_data["pm010_atm"],
                    "pm2dot5": pm_data["pm025_atm"],
                    "pm10": pm_data["pmq00_atm"],
                    "longitude": self.longitude,
                    "latitude": self.latitude,
                    "recorded": timestamp,
                }
            ]

        return data

    def publish(self, data):
        if data:
            print(f"Publishing to {self.linka_url} with: {data}")
            json_data = json.dumps(data)
            r = requests.post(self.linka_url, data=json_data, headers=self.headers)
        else:
            print("Unable to read data from sensor, not publishing")

    def run(self):
        while True:
            data = self.read_data()
            self.publish(data)
            time.sleep(300)
