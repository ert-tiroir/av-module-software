#
# Kalman Filter Algorithm
#
# Based on github.com/jarzebski/Arduino-KalmanFilter
#

import time

class KalmanFilter:
    def __init__(self, angle, bias, measure):
        self.Q_angle = angle
        self.Q_bias = bias
        self.R_measure = measure

        self.K_angle = 0
        self.K_bias = 0

        self.P = [[0, 0], [0, 0]]

        self.kt = time.time()

    def update(self, new_value, new_rate):
        dt = time.time() - self.kt

        self.K_rate = new_rate - self.K_bias
        self.K_angle += dt * self.K_rate

        self.P[0][0] += dt * (self.P[1][1] + self.P[0][1]) + self.Q_angle * dt
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        S = self.P[0][0] + self.R_measure

        self.K = [self.P[0][0] / S, self.P[1][0] / S]

        y = new_value - self.K_angle

        self.K_angle += self.K[0] * y
        self.K_bias += self.K[1] * y

        self.P[0][0] -= self.K[0] * self.P[0][0]
        self.P[0][1] -= self.K[0] * self.P[0][1]
        self.P[1][0] -= self.K[1] * self.P[0][0]
        self.P[1][1] -= self.K[1] * self.P[0][1]

        self.kt = time.time()

        return self.K_angle
