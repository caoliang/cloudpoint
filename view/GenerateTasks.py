import os
import sys
import math

def save_tasks(range_x, range_y, orientation, out_file):
    for pos_x, pos_y in zip(range_x, range_y):
        out_file.write("{0},{1},{2}\n".format(pos_x, pos_y, orientation))


target_file = os.path.join(os.path.join(os.getcwd(), "config"), "tracking_tasks.tmp.txt")

with open(target_file, 'w') as tf:
    # Orientation in anti-clockwise degree
    orientation_xy = 45
    x_range = range(0, -100, -10)
    y_range = range(0, -100, -10)
    save_tasks(x_range, y_range, orientation_xy, tf)

    orientation_xy = 135
    x_range = range(-100, -200, -10)
    y_range = range(-100, 0, 10)
    save_tasks(x_range, y_range, orientation_xy, tf)

    orientation_xy = 225
    x_range = range(-200, -100, 10)
    y_range = range(0, 100, 10)
    save_tasks(x_range, y_range, orientation_xy, tf)

    orientation_xy = 315
    x_range = range(-100, 0, 10)
    y_range = range(100, 0, -10)
    save_tasks(x_range, y_range, orientation_xy, tf)
