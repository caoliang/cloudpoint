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
    x_range = range(0, -300, -10)
    y_range = range(0, -300, -10)
    save_tasks(x_range, y_range, orientation_xy, tf)

    orientation_xy = 180
    x_range = [-300] * 30
    y_range = range(-300, 0, 10)
    save_tasks(x_range, y_range, orientation_xy, tf)

    orientation_xy = 270
    x_range = range(-300, 0, 10)
    y_range = [0] * 30
    save_tasks(x_range, y_range, orientation_xy, tf)
