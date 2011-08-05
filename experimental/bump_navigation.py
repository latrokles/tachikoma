#!/usr/bin/python
#
#
import sys
# the machine connected to the create has ROS installed so I just
# import the opencv installed by ROS (why am I not just using ROS ?)
try:
    from ros_path import python_path
    sys.path += python_path
except ImportError:
    print 'ROS is not installed on this machine...'

import create
import time
import random
import cv
from datetime import datetime

class VideoRecorder(object):

    def __init__(self):
        file = datetime.now().isoformat().replace(':','_').replace('T','__')
        self.camera   = cv.CaptureFromCAM(0)
        self.recorder = cv.CreateVideoWriter(
                                             file + '.mp4',
                                             cv.CV_FOURCC('M', 'P', '4', '2'),
                                             30,
                                             (320, 240),
                                             1
                                            )
    def record(self):
        while cv.WaitKey(33) != 27:
            frame = cv.QueryFrame(self.camera)
            cv.WriteFrame(self.recorder, frame)

PORT = '/dev/ttyUSB0'
class Tachikoma(object):
    '''
    '''
    def __init__(self, port):
        '''
        Instantiate Create object at port, set initial state variables, and
        start vision system.
        '''
        self.bot    = create.Create(port)
        self.stopped = True

    def forward(self, speed):
        '''
        Move forward at speed.
        '''
        self.bot.go(speed)
        self.stopped = False

    def backward(self, speed):
        '''
        Move backward at speed.
        '''
        self.bot.go(-speed)
        self.stopped = False

    def turn(self, direction, degrees):
        '''
        Turn in 'degrees' in 'direction'. Directions can be LEFT, RIGHT, or
        BACK (turn 180 degrees)
        '''
        # moving to the right needs negative value for degrees
        if direction == 'RIGHT': degrees = -degrees
        if direction == 'BACK': degrees = 180
        speed = degrees * 2
        self.bot.turn(degrees, speed)

    def check_and_avoid_collision(self):
        '''
        If left bumper is activated back away a bit and turn to the right, if
        right bumper is activated, back awaay and turn to the left.
        '''
        sensors = self.bot.sensors([create.LEFT_BUMP, create.RIGHT_BUMP])
        if sensors[create.LEFT_BUMP] == 1 and sensors[create.RIGHT_BUMP] == 0:
            self.avoid_collision('RIGHT')
        elif sensors[create.RIGHT_BUMP] == 1 and sensors[create.LEFT_BUMP] == 0:
            self.avoid_collision('LEFT')
        elif sensors[create.RIGHT_BUMP] ==1 and sensors[create.LEFT_BUMP] == 1:
            self.avoid_collision('BACK')

    def avoid_collision(self, direction):
        '''
        Back away and turn in direction.
        '''
        self.backward(30)
        time.sleep(0.5)
        self.turn(direction, 30)

    def stop(self):
        '''
        Stop robot.
        '''
        self.bot.stop()
        self.stopped = True

    def shutdown(self):
        '''
        Stops the robot (if it hasn't stopped before) and closes down the
        connection.
        '''
        if not self.stopped:
            self.stop()
        self.bot.close()

    def navigate(self):
        while True:
            self.forward(50)
            self.check_and_avoid_collision()

if __name__ == '__main__':
    max_bot = Tachikoma(PORT)
    try:
        max_bot.navigate()
    except KeyboardInterrupt:
        max_bot.stop()
        max_bot.shutdown()
