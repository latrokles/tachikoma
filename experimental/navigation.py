#!/usr/bin/python

import random
import tachikoma

def bump_navigation(robot):
    while True:
        robot.forward(50)
        robot.check_collisions()
        robot.avoid_collisions()

if __name__ == '__main__':
    max = tachikoma.Tachikoma(tachikoma.PORT)
    max.run(bump_navigation)
