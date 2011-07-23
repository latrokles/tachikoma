#!/usr/bin/python
#
#
import create
import time
import random

PORT = '/dev/ttyUSB0'
class Tachikoma(object):
    '''
    '''
    def __init__(self, port):
        self.robot = create.Create(port)
        self.speed = 0

    def set_speed(self, speed):
        '''
        Set the speed and move
        '''
        self.speed = speed
        self.robot.go(speed, 0)

    def forward(self, speed):
        if speed < 0: speed = -speed
        self.set_speed(speed)

    def backward(self, speed):
        if speed > 0: speed = -speed
        self.set_speed(speed)

    def turn(self, angle):
        self.robot.turn(angle, angle*2)

    def stop(self):
        self.robot.stop()

    def check_obstacle(self):
        sensor_values = self.robot.sensors([create.LEFT_BUMP, create.RIGHT_BUMP])
        if sensor_values[create.LEFT_BUMP] == 1 or sensor_values[create.RIGHT_BUMP] == 1:
            self.stop()
            self.backward(30)
            time.sleep(0.5)
            self.turn(random.choice([-30, 30, 180]))
            self.forward(30)

    def navigate(self):
        self.set_speed(40)
        while True:
            self.check_obstacle()

    def shutdown(self):
        self.set_speed(0)
        self.robot.close()

if __name__ == '__main__':
    max_bot = Tachikoma(PORT)
    try:
        max_bot.navigate()
    except KeyboardInterrupt:
        max_bot.stop()
        max_bot.shutdown()
