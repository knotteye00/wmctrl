#!/usr/bin/python
#
# wmctrl.py
#
# developed by Benjamin Hutchins and Ryan Stringham
#
# contributed by KnottEye
#
# an attempt to make linux more usable.
#
# MIT License
#
import sys
import os
import subprocess

# Customizable variables
window_title_height = 0#21
window_border_width = 1
panel_height = 30
leway_percentage = .05

debug = True

# Initialize, get data we need
def initialize():
    desk_output = subprocess.getoutput("wmctrl -d").split("\n")
    desk_list = [line.split()[0] for line in desk_output]

    current =  list(filter(lambda x: x.split()[1] == "*" , desk_output))[0].split()

    desktop = current[0]
    width =  current[8].split("x")[0]
    height =  current[8].split("x")[1]
    orig_x =  current[7].split(",")[0]
    orig_y =  current[7].split(",")[1]

    # this is unreliable, xdpyinfo often does not know what is focused, we use xdotool now
    #window_id = commands.getoutput("xdpyinfo | grep focus | grep -E -o 0x[0-9a-f]+").strip()
    #window_id = hex(int(window_id, 16))

    current = subprocess.getoutput("xwininfo -id $(xdotool getactivewindow)").split("\n")
    absoluteX = int(current[3].split(':')[1])
    absoluteY = int(current[4].split(':')[1])
    relativeX = int(current[5].split(':')[1])
    relativeY = int(current[6].split(':')[1])
    cW = int(current[7].split(':')[1])
    cH = int(current[8].split(':')[1])

    # Guess the panel height if we can, this has to assume your window is at the top of screen
    #global panel_height
    #if panel_height == 0 and (absoluteX - relativeX) > 0:
    #    panel_height = absoluteX - relativeX

    # this windows list is no longer needed
#    win_output = commands.getoutput("wmctrl -lG").split("\n")
#    win_list = {}
#
#    for line in win_output:
#        parts = line.split()
#        win_id = hex(int(parts[0], 16))
#        win_list[win_id] = {
#            'x': line[1],
#            'y': line[2],
#            'h': line[3],
#            'w': line[4],
#        }

    return (desktop,width,height, absoluteX, absoluteY, cW, cH)


# calculate these
(junk, max_width, max_height, cX, cY, cW, cH) = initialize()
max_width = int(max_width)
max_height = int(max_height)

# debug outputs
#print panel_height
#print cX, cY, cW, cH
#print max_width, max_height


def within_leway(w):
    global cW
    global leway_percentage

    leway = w * leway_percentage

    if cW - leway < w and cW + leway > w:
        return True
    else:
        return False



def maximize():
    command = "wmctrl -r :ACTIVE: -b toggle,maximized_vert,maximized_horz"
    os.system(command)


def unmaximize():
    command = "wmctrl -ir $(xdotool getactivewindow) -b remove,maximized_vert,maximized_horz"
    os.system(command)


def minimize():
    command = "xdotool getactivewindow windowminimize"
    os.system(command)


def move_active(x,y,w,h):
    unmaximize()

    if debug:
        print(x, y, w, h)

    # Sanity check, make sure bottom of window does not end up hidden
    if (y+h) > max_height:
        h = max_height - y

    if debug:
        print(x, y, w, h)

    #need to sanitize input so there's not trailing decimals
    x = str(x).split(".")[0]
    y = str(y).split(".")[0]
    w = str(w).split(".")[0]
    h = str(h).split(".")[0]

    if debug:
        print (y, w, h)

    command = "wmctrl -r :ACTIVE: -e 0," + str(x) + "," + str(y)+ "," + str(w) + "," + str(h)
    os.system(command)

    command = "wmctrl -a :ACTIVE: "
    os.system(command)


def left(shift = False):
    if shift:
        w = max_width/4
        if within_leway(w):
            w = w * 3
    else:
        w = max_width/2

    h = max_height - window_title_height
    move_active(0, panel_height, w - window_border_width, h)


def right(shift = False):
    if shift:
        w = max_width/4
        x = w * 3

        if within_leway(w):
            w = w * 3
    else:
        w = max_width/2
        x = max_width/2

    h = max_height - window_title_height
    move_active(x, panel_height, w - window_border_width, h)


def up(shift = False):
    if not shift:
        maximize()

    else:
        w = max_width - window_border_width
        h = max_height/2 - window_title_height - window_border_width
        move_active(0, panel_height, w, h)
 

def down(shift = False):
    if not shift:
        minimize()

    if shift:
        w = max_width - window_border_width
        h = max_height/2 - window_title_height - window_border_width
        y = max_height/2 + window_title_height + window_border_width
        move_active(0, y, w, h)


if __name__ == '__main__':
    cmd = sys.argv[1]

    if cmd == 'left':
        left()

    elif cmd == 'right':
        right()
    
    elif cmd in ('shift-left', 'left-shift'):
        left(True)
    
    elif cmd in ('shift-right', 'right-shift'):
        right(True)
    
    elif cmd in ('top', 'up'):
        up()

    elif cmd in ('shift-up', 'up-shift', 'shift-top', 'top-shift'):
        up(True)

    elif cmd in ('bottom', 'down'):
        down()

    elif cmd in ('shift-down', 'down-shift', 'shift-bottom', 'bottom-shift'):
        down(True)

    else:
        print("Unknown command passed:", cmd)
