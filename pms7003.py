"""
Library to communicate with a PMS7003 Sensor
Based on https://github.com/szczygiel-pawel/pms7003-python/blob/master/pms7003.py
"""
import sys
import time

if sys.platform in ["esp8266", "esp32"]:
    from machine import UART
elif sys.platform == "linux":
    from serial import Serial


class PMS7003:
    """Class for reading data from a PMS7003 sensor."""

    def __init__(self, port):
        self._frame_header = b"BM\x00\x1c"
        if sys.platform in ["esp8266", "esp32"]:
            self._connection = UART(
                port, baudrate=9600, bits=8, parity=None, stop=1, rxbuf=40
            )
        elif sys.platform == "linux":
            # Open serial port at "9600,8,N,1", no timeout
            self._connection = Serial(
                port,
                baudrate=9600,
                bytesize=EIGHTBITS,
                parity=PARITY_NONE,
                stopbits=STOPBITS_ONE,
                timeout=0.1,
            )
            self._connection.reset_input_buffer()
            self._connection.reset_output_buffer()

        self.set_passive_mode()
        self._processed_data = {
            "pm010_std": None,
            "pm025_std": None,
            "pm100_std": None,
            "pm010_atm": None,
            "pm025_atm": None,
            "pm100_atm": None,
            "part003": None,
            "part005": None,
            "part010": None,
            "part025": None,
            "part050": None,
            "part100": None,
        }

        self._raw_data = None
        self._checksum = None

    def __del__(self):
        self._connection.close()

    def _validate_frame(self):
        if (
            sum(self._frame_header) + sum(self._raw_data)
            == self._checksum[0] * 256 + self._checksum[1]
        ):
            return True
        return False

    def _read_frame_passive(self):
        cmd = b"\x42\x4d\xe2\x00\x00\x01\x71"
        self._connection.write(cmd)
        time.sleep(2)
        tmp_data = self._connection.read(32)
        self._raw_data = tmp_data[4:30]
        self._checksum = tmp_data[-2:]
        try:
            return self._validate_frame()
        except IndexError:
            return False

    def set_passive_mode(self):
        """Set sensor to passive mode."""
        while True:
            cmd = b"\x42\x4d\xe1\x00\x00\x01\x70"
            self._connection.write(cmd)
            time.sleep(1)
            result = self._connection.read(32)
            # Retry if answer frame is not correct
            if result == b"\x42\x4d\x00\x04\xe1\x00\x01\x74":
                break

    def set_active_mode(self):
        """Set sensor to active mode."""
        pass

    def set_sleep_mode(self):
        """Set sensor to sleep mode."""
        pass

    def set_wakeup_mode(self):
        """Set sensor to wake up mode."""
        pass

    def wakeup(self):
        """Wake up sensor."""
        cmd = b"\x42\x4d\xe4\x00\x01\x01\x74"
        self._connection.write(cmd)
        time.sleep(5)
        self._connection.read()

    def read(self):
        """Read data from sensor."""
        if self._read_frame_passive():
            self._processed_data["pm010_std"] = (
                self._raw_data[0] * 16 + self._raw_data[1]
            )
            self._processed_data["pm025_std"] = (
                self._raw_data[2] * 16 + self._raw_data[3]
            )
            self._processed_data["pm100_std"] = (
                self._raw_data[4] * 16 + self._raw_data[5]
            )
            self._processed_data["pm010_atm"] = (
                self._raw_data[6] * 16 + self._raw_data[7]
            )
            self._processed_data["pm025_atm"] = (
                self._raw_data[8] * 16 + self._raw_data[9]
            )
            self._processed_data["pm100_atm"] = (
                self._raw_data[10] * 16 + self._raw_data[11]
            )
            self._processed_data["part003"] = (
                self._raw_data[12] * 16 + self._raw_data[13]
            )
            self._processed_data["part005"] = (
                self._raw_data[14] * 16 + self._raw_data[15]
            )
            self._processed_data["part010"] = (
                self._raw_data[16] * 16 + self._raw_data[17]
            )
            self._processed_data["part025"] = (
                self._raw_data[18] * 16 + self._raw_data[19]
            )
            self._processed_data["part050"] = (
                self._raw_data[20] * 16 + self._raw_data[21]
            )
            self._processed_data["part100"] = (
                self._raw_data[22] * 16 + self._raw_data[23]
            )
            return self._processed_data

        return None


if __name__ == "__main__":
    if sys.platform in ["esp8266", "esp32"]:
        serial = 0
    elif sys.platform == "linux":
        serial = "/dev/ttyUSB0"

    sensor = PMS7003(serial)
    output = sensor.read()
    if output:
        print(output)
    else:
        print("Read error!")
