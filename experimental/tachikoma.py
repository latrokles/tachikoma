#!/usr/bin/python
#
#
import sys
import create
import random
import cv
import time

PORT = '/dev/ttyUSB0'

# directions for bumper
FRONT = 0
BACK  = 1
LEFT  = 2
RIGHT = 3

class Tachikoma(object):
    '''
    The robot!
    '''
    def __init__(self, port):
        '''
        Connect Create robot at port and set initial state
        variables.
        '''
        self.bot       = create.Create(port)
        self.stopped   = True
        self.curr_obstacle  = None  # current obstacle
        self.last_direction = None  # track the last direction we took
        self.last_seen      = 0     # track time of last obstacle

    def set_velocities(self, linear, turning):
        self.bot.go(linear, turning)

    def forward(self, speed):
        '''
        Move forward @ speed
        '''
        self.bot.go(speed)
        self.stopped = False

    def backward(self, speed):
        '''
        Move backward @ speed
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
        if direction == 'BACK':  degrees = random.randint(90, 270)
        speed = degrees * 2
        self.bot.turn(degrees, speed)

    def stop(self):
        '''
        Stop robot
        '''
        self.bot.stop()
        self.stopped = True

    def shutdown(self):
        '''
        Stops the robot and disconects it
        '''
        if not self.stopped:
            self.stop()
        self.bot.close()

    def check_collisions(self):
        '''
        If left bumper is activated back away a bit and turn to the right, if
        right bumper is activated, back awaay and turn to the left.
        '''
        sensors = self.bot.sensors([create.LEFT_BUMP, create.RIGHT_BUMP])
        if sensors[create.LEFT_BUMP] == 1 and sensors[create.RIGHT_BUMP] == 0:
            self.curr_obstacle = LEFT
            self.last_seen = time.time()
        elif sensors[create.RIGHT_BUMP] == 1 and sensors[create.LEFT_BUMP] == 0:
            self.curr_obstacle = RIGHT
            self.last_seen = time.time()
        elif sensors[create.RIGHT_BUMP] == 1 and sensors[create.LEFT_BUMP] == 1:
            self.curr_obstacle = FRONT
            self.last_seen = time.time()

    def get_current_obstacle(self):
        return self.curr_obstacle

    def avoid_collisions(self):
        '''
        Back away and turn in direction.
        '''
        direction = None
        now = time.time()
        if now - self.last_seen > 0.5:
            self.last_direction = None

        # set the direction we will go based on the obstacle we went in
        if self.curr_obstacle == LEFT:
            direction = 'RIGHT'
        elif self.curr_obstacle == RIGHT:
            direction = 'LEFT'
        elif self.curr_obstacle == FRONT:
            direction = 'BACK'
        # but... if we were moving in some direction before, continue going
        # that way
        if self.last_direction is not None:
            direction = self.last_direction

        # if there's some direction to turn, let's go
        if direction:
            self.last_direction = direction # set the last direction we went in
            self.stop()                     # stop
            self.backward(30)               # back away from obstacle
            time.sleep(0.5)
            self.turn(direction, 30)        # turn in the direction
            self.curr_obstacle = None       # clear the obstacle

    def run(self, behavior):
        '''
        Runs behavior on the robot.
        Behaviour function has to take a Tachikoma as parameter
        '''
        try:
            behavior(self)
        except KeyboardInterrupt:
            print('Finishing execution...')
        finally:
            print('Shutting down robot...')
            self.shutdown()
