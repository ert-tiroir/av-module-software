import time
import board
from adafruit_dps310.basic import DPS310

from core import CoreTarget
from logger import ModuleLogger, SUCCESS, INFO

from utils import pack_float, pack_int

i2c = board.I2C()   # uses board.SCL and board.SDA

dps310 = DPS310(i2c)

target = CoreTarget(
    "/tmp/sensors-module-output",
    "/tmp/sensors-module-input",
    "/tmp/sensors-logger"
)
logger = ModuleLogger(target)

logger.print(SUCCESS, "Succesfully started AV-Sensors")

while True:
    logger.print(INFO, "Temperature = %.2f *C"%dps310.temperature)
    logger.print(INFO, "Pressure = %.2f hPa"%dps310.pressure)
    
    target.write_string_to_core(
        bytes(
            [1]
          + pack_int  (int(time.time() * 1000000), 8)
          + pack_float(dps310.temperature)
          + pack_float(dps310.pressure)
          + pack_float(dps310.altitude)
        )
    )

    time.sleep(0.02)