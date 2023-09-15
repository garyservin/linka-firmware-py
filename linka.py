import sys
import time

if sys.platform in ["esp8266", "esp32"]:
    import machine
    import network
    import ntptime
    import ubinascii as binascii
    import ujson as json
    import urequests as requests
elif sys.platform == "linux":
    import binascii
    import json
    import requests
    import uuid

VERSION = "linka_mpv0.0.1"


class LinkaSensor:
    DEFAULT_PUBLISH_INTERVAL = 300  # seconds
    DEFAULT_SERVER_URL = "https://rald-dev.greenbeep.com/api/v1/measurements"

    def __init__(self, sensor, config):
        self.configure_network(config["ssid"], config["psk"])

        self.sensor = sensor
        self.sensor_id = self.get_mac()
        self.api_key = config["api_key"]
        self.description = config["description"]
        self.latitude = config["latitude"]
        self.longitude = config["longitude"]
        self.linka_url = config.get("linka_url", self.DEFAULT_SERVER_URL)
        self.interval = config.get("interval", self.DEFAULT_PUBLISH_INTERVAL)
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-api-key": self.api_key,
        }

        if sys.platform in ["esp8266", "esp32"]:
            self.led = machine.Pin(2, machine.Pin.OUT)

    @staticmethod
    def get_mac():
        """Get MAC address of the client."""
        if sys.platform in ["esp8266", "esp32"]:
            ap_if = network.WLAN(network.AP_IF)
            mac = binascii.hexlify(ap_if.config("mac")).decode()[-6:].upper()
        else:
            mac = str(uuid.getnode())[-6:]
        return mac

    @staticmethod
    def configure_network(ssid, psk):
        """Configure network if we're using a WiFi enabled board."""
        if sys.platform in ["esp8266", "esp32"]:
            sta_if = network.WLAN(network.STA_IF)
            sta_if.active(True)
            sta_if.connect(ssid, psk)
            while not sta_if.isconnected():
                time.sleep(1)

            # Configure time
            ntptime.settime()
        else:
            pass

    def read_data(self):
        """Read data from sensor."""
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
                    "pm10": pm_data["pm100_atm"],
                    "longitude": self.longitude,
                    "latitude": self.latitude,
                    "recorded": timestamp,
                }
            ]

        return data

    def publish(self, data):
        """Publish data to backend server."""
        if data:
            print(f"Publishing to {self.linka_url} with: {data}")
            if sys.platform in ["esp8266", "esp32"]:
                self.led.off()
            json_data = json.dumps(data)
            requests.post(self.linka_url, data=json_data, headers=self.headers)
            if sys.platform in ["esp8266", "esp32"]:
                self.led.on()
        else:
            print("Unable to read data from sensor, not publishing")

    def run(self):
        """Continues loop to read and publish data."""
        while True:
            data = self.read_data()
            self.publish(data)
            time.sleep(self.interval)
