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
MOVING_SPEED = 40 # cm/s
TURN_SPEED   = 30 # deg/s
SIZE  = WIDTH, HEIGHT = 480, 360
UI_BG = '../data/img/background.png'
FWD_ARROW = '../data/img/forward_arrow.png'
BCK_ARROW = '../data/img/backward_arrow.png'
LFT_ARROW = '../data/img/left_arrow.png'
RGT_ARROW = '../data/img/right_arrow.png'
OBSTACLE  = '../data/img/obstacle.png'
HORN_IMG  = '../data/img/sound.png'
HORN_SND  = '../data/audio/sound.wav'

FRONT = 0
BACK  = 1
LEFT  = 2
RIGHT = 3

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
        # setup for incoming instructions
        self.addr  = '0.0.0.0'
        self.port  = port
        self.robot = tachikoma.Tachikoma(tachikoma.PORT)
        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_in.bind((self.addr, self.port))

        # setup for outgoing sensor data
        self.client_addr = None
        self.client_port = 8075
        self.socket_out  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # a couple of vars to track robot state
        self.moving_velocity  = 0
        self.turning_velocity = 0

        # set the horn
        pygame.mixer.init()
        self.horn = pygame.mixer.Sound(HORN_SND)

        self.obstacle_data = {
                              FRONT: ['OFRT', 0],
                              LEFT:  ['OLFT', 0],
                              RIGHT: ['ORGT', 0],
                             }

    def read_sensor_data(self):
        obstacle = self.robot.get_current_obstacle()
        for sensor, data in self.obstacle_data.items():
            print 'SENSOR DATA: ', sensor, '--', data
            if sensor == obstacle:
                data[1] = 1
            else:
                data[1] = 0

    def send_sensor_data(self):
        if self.client_addr is not None:
            for sensor, data in self.obstacle_data.items():
                self.socket_out.send_to(
                                        ':'.join(data),
                                        (self.client_addr, self.client_port)
                                       )

    def receive_command(self):
        command, addr = self.socket_in.recvfrom(1024)
        if self.client_addr is None:
            self.client_addr = addr[0]
        self.handle_command(command)

    def handle_command(self, command):
        # handle all the moving stuff
        if command == 'FWD':
            self.moving_velocity = MOVING_SPEED
        if command == 'BCK':
            self.moving_velocity = -MOVING_SPEED
        if command == 'LFT':
            self.turning_velocity = TURN_SPEED
        if command == 'RGT':
            self.turning_velocity = -TURN_SPEED

        if command == 'STPM':
            self.moving_velocity  = 0
        if command == 'STPT':
            self.turning_velocity = 0
        self.robot.set_velocities(self.moving_velocity, self.turning_velocity)

        # handle honking
        if command == 'HNK':
            self.honk()

    def honk(self):
        self.horn.play()

    def run(self):
        while True:
            self.receive_command()
            self.read_sensor_data()
            self.send_sensor_data()

class TeleoperationClient(object):
    '''
    Receives input from user and converts it into instructions that are sent
    to the TeleoperationServer running on the robot. It also displays sensor
    and battery data that it receives from the TeleoperationServer.
    '''
    def __init__(self, server_addr, server_port=8075):
        # connection out to server
        self.server_addr = server_addr
        self.server_port = server_port
        self.socket_out  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # send instructions to server
        # connection in from server
        self.addr      = '0.0.0.0'
        self.port      = 8075     # hmmm, we'll use the same one for now
        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # read data back from server
        self.socket_in.bind((self.addr, self.port))

        # create our window and UI stuff
        self.window      = pygame.display.set_mode(SIZE)
        self.background  = pygame.image.load(UI_BG)
        self.widgets = {
                        'FWD':[load_image(FWD_ARROW), ((WIDTH/2) - 50, 20), 0],
                        'BCK':[load_image(BCK_ARROW), ((WIDTH/2) - 50, 120), 0],
                        'LFT':[load_image(LFT_ARROW), (WIDTH - 120, 20), 0],
                        'RGT':[load_image(RGT_ARROW), (20, 20), 0],
                        'HNK':[load_image(HORN_IMG), ((WIDTH/2) - 50, 180), 0],
                        'OLFT':[load_image(OBSTACLE), (20, 20), 0],
                        'ORGT':[load_image(OBSTACLE), (WIDTH - 120, 20), 0],
                        'OFRT':[load_image(OBSTACLE), ((WIDTH/2) - 50, 20), 0],
                       }
        pygame.display.set_caption('Teleoperation Client: ' + self.server_addr)
        self.display_ui()

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
        if command == 'STPM':
            self.widgets['FWD'][2] = 0
            self.widgets['BCK'][2] = 0
        elif command == 'STPT':
            self.widgets['LFT'][2] = 0
            self.widgets['RGT'][2] = 0
        elif command == 'STPH':
            self.widgets['HNK'][2] = 0
        else:
            self.widgets[command][2] = 1

    def receive_sensor_data(self):
        '''
        Receive robot data from the TeleoperationServer.
        '''
        data, srv_addr = self.socket_in.recvfrom(1024)
        if srv_addr[0] == self.server_addr:
            self.handle_sensor_data(data)

    def handle_sensor_data(self, sensor_data):
        '''
        Handle the sensor data received from TeleoperationServer
        '''
        sensor, value = sensor_data.split(':')
        self.widgets[sensor][2] = int(value)

    def display_ui(self):
        '''
        Displays UI widgets on the screen, based on their state
        '''
        self.window.blit(self.background, (0, 20))
        for name, widget in self.widgets.items():
            if widget[2]:
                self.window.blit(widget[0], widget[1])

    def run(self):
        while True:
            # get events and process them accordingly
            for event in pygame.event.get():
                self.process_event(event)
            self.receive_sensor_data()
            self.display_ui()
            pygame.display.flip()

if __name__ == '__main__':
    if sys.argv[1] == 'client':
        addr = sys.argv[2]
        client = TeleoperationClient(addr)
        client.run()
    elif sys.argv[1] == 'server':
        server = TeleoperationServer()
        server.run()
