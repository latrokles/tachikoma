#!/usr/bin/python
#
#

import sys
try:
    from ros_path import python_path
    sys.path += python_path
except ImportError:
    print 'ROS is not installed on this machine...'
import create
import cv
import math
import time

#simple test
'''
Implement simple color tracking, robot turns around to keep track of the object
'''

PORT       = '/dev/ttyUSB0'
SIZE       = WIDTH, HEIGHT = 320, 240
CENTER     = CX, CY = WIDTH / 2, HEIGHT / 2
MIN_OFFSET = 50 # defines a range for the robot's center view
FWD_SPEED  = 50

def main():
    camera = cv.CaptureFromCAM(0)
    max    = create.Create(PORT)
    try:
        # create a smaller image to resize the original frame into
        frame = cv.QueryFrame(camera)
        small = cv.CreateImage(SIZE, cv.IPL_DEPTH_8U, 3)
        while True:
            frame = cv.QueryFrame(camera)
            cv.Resize(frame, small)
            # get x,  y coordinates for target
            target_x, target_y = get_object_position(small)

            # determine how far off is the robot's heading from the target
            print '(CX, target_x) : ', (CX, target_x)
            distance = CX - target_x

            # turn rate should be better defined
            if math.fabs(distance) < MIN_OFFSET:
                turn_rate = 0
            else:
                turn_rate = (float(distance) / WIDTH) * 60
            max.go(FWD_SPEED, turn_rate)
    except KeyboardInterrupt:
        print 'leaving now...'
    finally:
        print 'Stopping robot...'
        print 'Shutting down robot..'
        print 'Bye!'
        max.stop()
        max.close()
        sys.exit(0)

def get_object_position(img):
    '''
    Gets an image and returns the x, y position of the red object found in it.
    '''
    red_object   = detect_red(img)
    bounding_box = get_bounding_box(red_object)
    object_pos   = get_rect_pos(bounding_box)
    return object_pos

def get_rect_pos(bounding_rect):
    '''
    Takes a rectangle and returns it's center position as a (x, y) tuple
    '''
    # if bounding rect has no size == 0, then position is on center
    # something tells me this should be elsewhere though
    if bounding_rect == (0, 0, 0, 0):
        x, y = CX, CY
    else:
        corner_x, corner_y = bounding_rect[0], bounding_rect[1]
        width, height      = bounding_rect[2], bounding_rect[3]
        x = corner_x + (width / 2)
        y = corner_y + (height / 2)
    return x, y

def get_bounding_box(img):
    '''
    Takes an image and returns a tuple with the bounding boxes (a cvRect) for
    any red objects in it (right now it does a single box for all red objects,
    but that will change when I do contour detection.
    '''
    matrix = cv.GetMat(img)
    bounding_box = cv.BoundingRect(matrix)
    return bounding_box

def detect_red(img):
    '''
    Takes an image and returns a thresholded image for the color red
    '''
    img_size = cv.GetSize(img)
    red   = cv.CreateImage(img_size, cv.IPL_DEPTH_8U, 1)
    blue  = cv.CreateImage(img_size, cv.IPL_DEPTH_8U, 1)
    green = cv.CreateImage(img_size, cv.IPL_DEPTH_8U, 1)

    cv.Split(img, blue, green, red, None)

    # substract the green and blue from red
    cv.Add(blue, green, green)
    cv.Sub(red, green, red)

    # apply the threshold to img
    cv.Threshold(red, red, 50, 255, cv.CV_THRESH_BINARY)
    return red

if __name__ == '__main__':
    main()
