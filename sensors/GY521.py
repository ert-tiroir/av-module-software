

from d.abstract import AbstractDevice

import adafruit_mpu6050
import time

from sensors.kalman import KalmanFilter


# ======================================================================================
# ======================================= DEVICE =======================================
# ======================================================================================

class GY521Device(AbstractDevice):
    def __init__(self, context):
        self.gy521 = adafruit_mpu6050.MPU6050(context.i2c)

        self.rotation         = vector(0, 0, 0)
        self.angular_velocity = vector(0, 0, 0)

        self.rx = KalmanFilter(0.001, 0.003, 0.03)
        self.ry = KalmanFilter(0.001, 0.003, 0.03)
        self.rz = KalmanFilter(0.001, 0.003, 0.03)

        self.time = time.time()
    def rotation_matrix (self):
        return rotation(self.rotation.array[0][0],
                        self.rotation.array[1][0],
                        0)
    def is_query(self, query):
        return query == "0x68"
    def query(self, query):
        new_time  = time.time()
        dt        = new_time - self.time
        self.time = new_time

        gyro = self.gy521.gyro
        gyro = [
            self.rx.update(gyro[0], gyro[0]),
            self.ry.update(gyro[1], gyro[1]),
            self.rz.update(gyro[2], gyro[2])
        ]
        angular_acceleration =  self.rotation_matrix() * vector(*gyro)

        self.angular_velocity = self.angular_velocity + dt * angular_acceleration
        self.rotation         = self.rotation         + dt * self.angular_velocity
        
        return f"{self.rotation.array[0][0]} {self.rotation.array[1][0]} {self.rotation.array[2][0]}"
        # T|P|H\n
