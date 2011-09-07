#!/usr/bin/python
#
'''
Remote operation of the irobot create robot in the form of a server that receives
command instructions and a client (with a graphical interface) that issues them.

The commands are rather simple at the moment:
    - FWD:  start moving forward
    - BCK:  start moving backward
    - RGT:  start turning right
    - LFT:  start turning left
    - STPM: stop moving (forward/backward)
    - STPT: stop turning (left/right)
    - HNK:  sound the horn

As for the data sent by the robot:
    - OLFT: indicates there's an obstacle to the left (0 or 1)
    - ORGT: indicates there's an obstacle on the right (0 or 1)
    - OFRT: indicates there's an obstacle completely in front (0 or 1)
    - BATT: battery (0-100)
'''
import sys
import json
import socket
import tachikoma
import pygame
from pygame.locals import *

## -- SOME GLOBALS -- ##
MOVING_SPEED = 20 # cm/s
TURN_SPEED   = 10 # deg/s
SIZE  = WIDTH, HEIGHT = 480, 360
UI_BG = '../data/img/background.png'
FWD_ARROW = '../data/img/forward_arrow.jpg'
BCK_ARROW = '../data/img/backward_arrow.jpg'
LFT_ARROW = '../data/img/left_arrow.jpg'
RGT_ARROW = '../data/img/right_arrow.jpg'

def load_image(img_file):
    '''
    Returns a pygame surface for img_file
    '''
    img = pygame.image.load(img_file).convert()
    img.set_colorkey((0, 0, 0), RLEACCEL)
    return img

class TeleoperationServer(object):
    '''
    Receives instructions from the TeleoperationClient and controls the robot
    accordingly. It also queries the robot for data about its sensors and
    battery life (just another sensor) and sends it to the TeleoperationClient
    so that the operator is aware of the state of the robot.
    '''
    def __init__(self, port=8075):
        self.addr  = '0.0.0.0'
        self.port  = port
        #self.robot = tachikoma.Tachikoma(tachikoma.PORT)
        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_in.bind((self.addr, self.port))

    def receive_command(self):
        command, addr = self.socket_in.recvfrom(1024)
        print(command + "from ", addr)

    def run(self):
        while True:
            self.receive_command()


class TeleoperationClient(object):
    '''
    Receives input from user and converts it into instructions that are sent
    to the TeleoperationServer running on the robot. It also displays sensor
    and battery data that it receives from the TeleoperationServer.
    '''
    def __init__(self, server_addr, server_port=8075):
        self.server_addr = server_addr
        self.server_port = server_port
        self.socket_out  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # create our window and UI stuff
        self.window      = pygame.display.set_mode(SIZE)
        self.background  = pygame.image.load(UI_BG)
        self.ui_elements = {
                           'FWD':(load_image(FWD_ARROW), ((WIDTH/2) - 50, 20)),
                           'BCK':(load_image(BCK_ARROW), ((WIDTH/2) - 50, 120)),
                           'LFT':(load_image(LFT_ARROW), (WIDTH - 120, 20)),
                           'RGT':(load_image(RGT_ARROW), (20, 20)),
                           'HNK':(load_image(RGT_ARROW), ((WIDTH/2) - 50, 180)),
                           }
        pygame.display.set_caption('Teleoperation Client: ' + self.server_addr)
        self.clear_ui()

    def process_event(self, event):
        '''
        Process the input events from the graphical interface and convert them
        into instructions for the robot.
        '''
        #print(event) # a bit of debugging data
        if event.type == pygame.QUIT: sys.exit(0)  # handle termination first
        if event.type == KEYDOWN:
            if event.key == K_UP:    self.send_command('FWD')
            if event.key == K_DOWN:  self.send_command('BCK')
            if event.key == K_LEFT:  self.send_command('LFT')
            if event.key == K_RIGHT: self.send_command('RGT')
            if event.key == K_SPACE: self.send_command('HNK')

        if event.type == KEYUP:
            if event.key == K_UP or event.key == K_DOWN:
                self.send_command('STPM')
            if event.key == K_LEFT or event.key == K_RIGHT:
                self.send_command('STPT')
            if event.key == K_SPACE:
                self.send_command('STPH')

    def send_command(self, command):
        '''
        Sends the command over the network and updates UI
        '''
        self.socket_out.sendto(command, (self.server_addr, self.server_port))
        if command[:3] == 'STP':
            self.clear_ui()
        else:
            ui_element = self.ui_elements[command]
            self.window.blit(ui_element[0], ui_element[1])

    def clear_ui(self):
        '''
        Clears the UI indicators
        '''
        self.window.blit(self.background, (0, 20))

    def run(self):
        while True:
            # get events and process them accordingly
            for event in pygame.event.get():
                self.process_event(event)
            pygame.display.flip()

if __name__ == '__main__':
    if sys.argv[1] == 'client':
        addr = sys.argv[2]
        client = TeleoperationClient(addr)
        client.run()
    elif sys.argv[1] == 'server':
        server = TeleoperationServer()
        server.run()
