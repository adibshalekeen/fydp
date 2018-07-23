import sys
import subprocess
from picamera import PiCamera
from time import sleep
import numpy as np

camera = PiCamera()
camera.rotation = 180
camera.resolution = (100, 100)


CONST_NOTHING = 0
CONST_RED = 1
CONST_GREEN = 2
CONST_BLUE = 3

current_color = CONST_NOTHING

def colorChange(current_color, color, ip):
    sys.stdout.write('change happen\n')
    if current_color != color:
        current_color = color
        sys.stdout.write(str(current_color) + '\n')
        if color != CONST_NOTHING:
            sys.stdout.write('send request\n')
            #send color change request
            if color == CONST_RED:
                subprocess.call('./on.sh ' + ip, shell=True)
            else:
                subprocess.call('./off.sh ' + ip, shell=True)


    return current_color

ip = sys.argv[1]

while(True):
    output = np.empty((112, 128, 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    output = output.reshape((112, 128, 3))
    output = output[:100, :100, :]
    red = output[: , :, 0].sum() / (100*100)
    green = output[: , :, 1].sum() / (100*100)
    blue = output[: , :, 2].sum() / (100*100)
    average = (red + green + blue) / 3
    average = average * 1.2
    if red > average:
        current_color = colorChange(current_color, CONST_RED, ip)
    elif green > average:
        current_color = colorChange(current_color, CONST_GREEN, ip)
    elif blue > average:
        current_color = colorChange(current_color, CONST_BLUE, ip)
    else:
        current_color = colorChange(current_color, CONST_NOTHING, ip)
    sleep(1)
