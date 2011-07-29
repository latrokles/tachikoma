#!/usr/bin/python


import socket
import sys
import cv
import bz2

win_name = 'video'
window   = cv.NamedWindow(win_name)
HOST, PORT = 'localhost', 9999
PACKET_SIZE = 1024
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto('CONNECT', (HOST,PORT))
while cv.WaitKey(33) != 27:
    img_chunks = [ ]
    new_frame = True
    while new_frame:
        chunk = sock.recv(PACKET_SIZE)
        if chunk == 'DONE':
            new_frame = False
        else:
            img_chunks.append(chunk)
    byte_str = ''.join(img_chunks)
    img = cv.CreateImage((320, 240), cv.IPL_DEPTH_8U, 3)
    cv.SetData(img, byte_str)
    cv.ShowImage(win_name, img)
    sock.sendto('READY', (HOST, PORT))
    #print 'CLIENT: done with frame, sent ready for next frame'
