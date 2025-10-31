#!/usr/bin/env python3
#############################################################################
# Filename    : LEDMatrix.py
# Description : Control LEDMatrix with 74HC595
# auther      : www.freenove.com
# modification: 2019/12/28
########################################################################
import RPi.GPIO as GPIO
import time

LSBFIRST = 1
MSBFIRST = 2
# define the pins connect to 74HC595
dataPin   = 11      # DS Pin of 74HC595(Pin14)
latchPin  = 13      # ST_CP Pin of 74HC595(Pin12)
clockPin = 15       # SH_CP Pin of 74HC595(Pin11)
rawpic = [0, 31, 31, 31, 0, 0, 0, 0]
sobelpic = [31, 255, 31, 255, 255, 255, 255, 31]
cannypic = [105, 81, 139, 80, 100, 73, 136, 41]
data = [     # data
    rawpic, # "binarypic"
    sobelpic, # "sobelpic"
    cannypic, # "cannypic"
    0x00, 0x00, 0x7F, 0x49, 0x49, 0x36, 0x00, 0x00, # "B"
    0x00, 0x00, 0x46, 0x49, 0x49, 0x31, 0x00, 0x00  # "S"
    0x00, 0x00, 0x3E, 0x41, 0x41, 0x22, 0x00, 0x00, # "C"
]
def setup():
    GPIO.setmode(GPIO.BOARD)    # use PHYSICAL GPIO Numbering
    GPIO.setup(dataPin, GPIO.OUT)
    GPIO.setup(latchPin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)

def shiftOut(dPin,cPin,order,val):
    for i in range(0,8):
        GPIO.output(cPin,GPIO.LOW);
        if(order == LSBFIRST):
            GPIO.output(dPin,(0x01&(val>>i)==0x01) and GPIO.HIGH or GPIO.LOW)
        elif(order == MSBFIRST):
            GPIO.output(dPin,(0x80&(val<<i)==0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin,GPIO.HIGH);

def loop():
    while True:
        for j in range(0,500): # Repeat enough times to display the patterns for a while
            """Display each entry in data for 10 seconds, with a 0.5 second blank between alternations, and display B, S, C for only 2 seconds each
            Display B before binary, S before sobel, etc."""

def destroy():
    GPIO.cleanup()
if __name__ == '__main__':  # Program entrance
    print ('Program is starting...' )
    setup()
    try:
        loop()
    except KeyboardInterrupt:   # Press ctrl-c to end the program.
        destroy()
