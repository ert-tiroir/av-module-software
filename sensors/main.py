import time
import board
from adafruit_dps310.basic import DPS310

import GY521
from core import CoreTarget
from logger import WARNING, ModuleLogger, SUCCESS, INFO, ERROR

from utils import pack_float, pack_int

i2c = board.I2C()   # uses board.SCL and board.SDA

target = CoreTarget(
    "/tmp/sensors-module-output",
    "/tmp/sensors-module-input",
    "/tmp/sensors-logger"
)
logger = ModuleLogger(target)

logger.print(SUCCESS, "Succesfully started AV-Sensors")

try:
    dps310 = DPS310(i2c)
except Exception:
    dps310 = None
    logger.print(ERROR, "Could not start DPS310")

try: 
    gy521 = GY521(i2c)
except Exception:
    gy521 = None
    logger.print(ERROR, "Could not start GY521")



lastDPS310_WARNING = 0
lastGY521_WARNING = 0

buffer  = b""
running = False

def write_to_buffer (bytes):
    if len(buffer) + len(bytes) > 1016:
        target.write_string_to_core(buffer)
        buffer = b""
    buffer += bytes

while True:
    found, command = target.read_string_from_core()
    if found:
        if command == b"START": 
            running = True
            logger.print(SUCCESS, "Successfully started sensors")
        else:
            running = False
            logger.print(SUCCESS, "Successfully stopped sensors")

    if not running: continue

    try:

        logger.print(INFO, "Temperature = %.2f *C"%dps310.temperature)
        logger.print(INFO, "Pressure = %.2f hPa"%dps310.pressure)
        logger.print(INFO, "Altitude = %.2f m"%dps310.altitude)



        write_to_buffer(
            bytes(
                [1]
            + pack_int  (int(time.time() * 1000000), 8)
            + pack_float(dps310.temperature)
            + pack_float(dps310.pressure)
            + pack_float(dps310.altitude)
            )
        )
    except Exception:
        if time.time() - lastDPS310_WARNING >= 3:
            lastDPS310_WARNING = time.time()
            logger.print(WARNING, "Could not read data from DPS310")


    try:
        value = gy521.query()
        ## ???
        logger.print(INFO, "Vx = %.2f m/s"v)
        logger.print(INFO, "Vy = %.2f m/s"%)
        logger.print(INFO, "Vz = %.2f m/s"%)


##???
        write_to_buffer(
            bytes(
                [1]
            + pack_int  (int(time.time() * 1000000), 8)
            + pack_float()
            + pack_float()
            + pack_float()
            )
        )
    except Exception:
        if time.time() - lastGY521_WARNING >= 3:
            astGY521_WARNING = time.time()
            logger.print(WARNING, "Could not read data from GY521")        

    time.sleep(0.02)
