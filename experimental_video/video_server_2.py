#!/usr/bin/python
#

import socket
import cv
import bz2

HOST, PORT  = 'localhost', 9999
PACKET_SIZE = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
msg, address = server.recvfrom(PACKET_SIZE)
if msg == 'CONNECT':
    camera = cv.CaptureFromCAM(0)
    while True:
        frame = cv.QueryFrame(camera)
        small_frame = cv.CreateImage((320, 240), cv.IPL_DEPTH_8U, 3)
        cv.Resize(frame, small_frame)
        byte_str = small_frame.tostring()
        number_of_chunks = len(byte_str) / PACKET_SIZE
        if len(byte_str) % PACKET_SIZE != 0: number_of_chunks += 1
        idx1, idx2 = 0, 0 + PACKET_SIZE
        for i in range(number_of_chunks):
            chunk = byte_str[idx1:idx2]
            server.sendto(chunk, address)
            idx1, idx2 = idx2, idx2 + PACKET_SIZE
            if idx2 >= len(byte_str): idx2 = len(byte_str)
        server.sendto('DONE', address)
        print 'SERVER: send end of frame, awaiting ready for next frame response'
        confirmation = server.recv(PACKET_SIZE)
