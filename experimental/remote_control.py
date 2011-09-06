#!/usr/bin/python
#
'''
Remote operation of the irobot create robot in the form of a server that receives
command instructions and a client (with a graphical interface) that issues them.
'''
import sys
import json
import socket
import pygame
from pygame.locals import *

## -- SOME GLOBALS -- ##
MOVING_SPEED = 20 # cm/s
TURN_SPEED   = 10 # deg/s
SIZE  = WIDTH, HEIGHT = 480, 320
UI_BG = '../data/img/background.png'

class TeleoperationServer(object):
    pass


class TeleoperationClient(object):
    '''
    Receives input from user and converts it into instructions that are sent
    to the TeleoperationServer running on the robot. It also displays sensor
    and battery data that it receives from the TeleoperationServer.
    '''
    def __init__(self, server_addr, server_port=8075):
        self.server_addr = server_addr
        self.server_port = server_port
        # create our window
        self.window      = pygame.display.set_mode(SIZE)
        self.background  = pygame.image.load(UI_BG)
        pygame.display.set_caption('Teleoperation Client: ' + self.server_addr)

    def process_event(self, event):
        '''
        Process the input events from the graphical interface and convert them
        into instructions for the robot.
        '''
        #print(event) # a bit of debugging data
        if event.type == pygame.QUIT: sys.exit(0)  # handle termination first
        if event.type == KEYDOWN:
            if event.key == K_UP:    print('Move forward')
            if event.key == K_DOWN:  print('Move backward')
            if event.key == K_LEFT:  print('Turning left')
            if event.key == K_RIGHT: print('Turning right')
            if event.key == K_SPACE: print('honk')
        if event.type == KEYUP:
            if event.key == K_UP:    print('stop forward')
            if event.key == K_DOWN:  print('stop backward')
            if event.key == K_LEFT:  print('stop urning left')
            if event.key == K_RIGHT: print('stop Turning right')

    def display_ui_elements(self):
        '''
        Displays the different UI elements on the screen.
        '''
        pass

    def run(self):
        while True:
            # get events and process them accordingly
            for event in pygame.event.get():
                self.process_event(event)
            self.window.blit(self.background, (0, 0))
            #pygame.draw.rect(self.window, (255, 255, 255), (20, 20, 100, 100))
            pygame.display.flip()

if __name__ == '__main__':
    client = TeleoperationClient('0.0.0.0')
    client.run()
