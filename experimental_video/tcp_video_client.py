#!/usr/bin/python
#
#
import socket
import cv
import sys

win_name = 'video'
window   = cv.NamedWindow(win_name)
ADDRESS  = HOST, PORT = 'localhost', 9999
BUFFER_SIZE = 230400

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

while cv.WaitKey(33) != 27:
    data = client.recv(BUFFER_SIZE)
    img = cv.CreateImage((320, 240), cv.IPL_DEPTH_8U, 3)
    cv.SetData(img, data)
    cv.ShowImage(win_name, img)
    client.send('READY')
client.send('CLOSE')
sys.exit(0)
