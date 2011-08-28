#!/usr/bin/python
#
#
import sys
import create
import random
import cv
import time

PORT = '/dev/ttyUSB0'
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
        self.obstacles = {'LEFT':0, 'RIGHT':0} # track previous obstacles
        self.last_seen = 0                   # track time of last obstacle

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
        if direction == 'BACK': degrees = 180
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
            self.obstacles['LEFT']  += 1
            self.last_seen = time.time()
        elif sensors[create.RIGHT_BUMP] == 1 and sensors[create.LEFT_BUMP] == 0:
            self.obstacles['RIGHT'] += 1
            self.last_seen = time.time()
        elif sensors[create.RIGHT_BUMP] ==1 and sensors[create.LEFT_BUMP] == 1:
            self.obstacles['BACK']  += 1
            self.last_seen = time.time()

    def avoid_collisions(self):
        '''
        Back away and turn in direction.
        '''
        now = time.time()
        if now - self.last_seen > 3:
            self.obstacles['BACK']  = 0
            self.obstacles['LEFT']  = 0
            self.obstacles['RIGHT'] = 0

        if self.obstacles['BACK'] or self.obstacles['LEFT'] or self.obstacles['RIGHT']:
            # there's an obstacle, turn to where there are the least amount of obstacles
            min_hits  = 10000
            way_to_go = None
            for direction, hits in self.obstacles.items():
                if hits < min_hits:
                    way_to_go = direction
            self.backward(30)
            time.sleep(0.5)
            self.turn(way_to_go, 30)

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
            self.shutdown()
