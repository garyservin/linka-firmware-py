from config import config
from linka import LinkaSensor
from pms7003 import PMS7003

def run():
    sensor = PMS7003(config.get("serial_port", 0))

    linka = LinkaSensor(sensor, config)

    linka.run()


if __name__ == "__main__":
    run()
