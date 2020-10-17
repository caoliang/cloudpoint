import os
import sys


def save_tasks(range_x, range_y, out_file):
    for pos_x, pos_y in zip(range_x, range_y):
        out_file.write("{0},{1}\n".format(pos_x, pos_y))


target_file = os.path.join(os.path.join(os.getcwd(), "config"), "tracking_tasks.tmp.txt")

with open(target_file, 'w') as tf:
    x_range = range(0, -300, -10)
    y_range = range(0, -300, -10)
    save_tasks(x_range, y_range, tf)

    x_range = range(-300, -270, 1)
    y_range = range(-300, 0, 10)
    save_tasks(x_range, y_range, tf)

    x_range = range(-270, 0, 10)
    y_range = range(0, 27, 1)
    save_tasks(x_range, y_range, tf)

    x_range = range(0, -100, -10)
    y_range = range(27, -17, -1)
    save_tasks(x_range, y_range, tf)

    x_range = range(-100, 0, 10)
    y_range = range(0, -100, -10)

    save_tasks(x_range, y_range, tf)

    x_range = range(0, 100, 10)
    y_range = range(-100, 0, 10)

    save_tasks(x_range, y_range, tf)

    x_range = range(100, 0, -10)
    y_range = range(0, 100, 10)

    save_tasks(x_range, y_range, tf)

    x_range = range(0, -100, -10)
    y_range = range(100, 0, -10)

    save_tasks(x_range, y_range, tf)
