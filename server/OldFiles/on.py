import RPi.GPIO as gpio 
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.setup(13, gpio.OUT)
gpio.setup(22, gpio.OUT)
gpio.output(13, 1)
gpio.output(22, 0)
