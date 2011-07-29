#!/usr/bin/python
#
# Quick streaming video server using opencv, not particularly efficient though.
#
#

import SocketServer
import cv
import bz2

PACKET_SIZE = 1024
class VideoStreamer(SocketServer.BaseRequestHandler):

    def handle(self):
        initial_msg   = self.request[0].strip()
        socket        = self.request[1]
        if initial_msg == 'CONNECT':
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
                    socket.sendto(chunk, self.client_address)
                    idx1, idx2 = idx2, idx2 + PACKET_SIZE
                    if idx2 >= len(byte_str): idx2 = len(byte_str)
                # send DONE marker
                socket.sendto('DONE', self.client_address)

if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999
    server = SocketServer.UDPServer((HOST, PORT), VideoStreamer)
    server.serve_forever()
