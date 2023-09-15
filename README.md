# linka-firmware-py
A Micropython Library for Linka Air Quality Sensors

## Important Note
Micropython doesn't support a Software Serial implementation, so the sensor needs to be connected to the Hardware Serial pins on a ESP8266, this works differently from https://github.com/garyservin/linka-firmware and requires changing the cables on the board if you were using that before. Connection diagram TBA.

## Installation
### Installing micropython
1. Download the latest version of micrpython from [micropyton.org](https://micropython.org/download/) for your specific board. 
2. Install the flash utility with `pip3 install --user esptool`
3. Erase the flash with `esptool.py --port /dev/ttyUSB0 erase_flash`. You might need to specify a different port depending on your setup.
4. Flash the micropython firmware with ```esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dout 0 MICROPYTHON_FIRWMARE.bin```. Replace `MICROPYTHON_FIRWMARE.bin` with the correct filename.

### Create your config file
Create a config file with your custom credentials, it should look like this
```
config = {
    "ssid": "YOUR_WIFI_SSID",
    "psk": "YOUR_WIFI_PASSWORD",

    "api_key": "YOUR_SUPER_SECRET_API_KEY",

    "latitude": 0.0000,
    "longitude": 0.0000,

    "description": "My Sensor",
}
```
Other options include
- linka_url   # if you want to point to a custom backend server, defaults to https://rald-dev.greenbeep.com/api/v1/measurements if not specified
- interval    # time in seconds to wait before reading and sending a new measuerement

### Installing te linka python code
1. Install the ampy tool `pip3 install --user adafuit-ampy`
2. Copy the files to your microcontroller
```
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put linka.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put pms7003.py
ampy --port /dev/ttyUSB0 put webrepl_cfg.py
```
3. Restart your board with `ampy --port /dev/ttyUSB0 reset`
4. The LED on the board will blink every 5 minutes showing that the board is sending data, if not, you can try to debug it by using a webrepl client like the one included with thonny.

## TODO
- [ ] Add captive portal to more easily configure WiFi credentials
- [ ] Store data if board isn't connected to the internet to send when connected
- [ ] Simplify flashing method, add web flashing option
- [ ] Confirm code works with with ESP32
- [ ] Confirm code works with Raspberry Pi Pico W
- [ ] Create wiring diagram
