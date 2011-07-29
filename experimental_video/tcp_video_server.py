#!/usr/bin/python

import sys
try:
    from ros_path import python_path
    sys.path += python_path
except ImportError:
    print 'ROS Path does not exist... resumin normally'

import cv
import socket

ADDRESS     = HOST, PORT  = 'localhost', 9999
BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
server.listen(1)
print 'listening...'

connection, addr = server.accept()
print 'connected to %s!' % (addr,)
camera = cv.CaptureFromCAM(0)
while True:
    frame = cv.QueryFrame(camera)
    small_frame = cv.CreateImage((320, 240), cv.IPL_DEPTH_8U, 3)
    cv.Resize(frame, small_frame)
    byte_str = small_frame.tostring()

    # split
    connection.send(byte_str)
    msg = connection.recv(1024)
    if msg == 'CLOSE':
        break
print 'closing socket'
connection.close()
sys.exit(0)

