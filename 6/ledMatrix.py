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
def reverseBits(byte):
    """Reverse the bits in a byte (mirror horizontally)."""
    result = 0
    for i in range(8):
        if byte & (1 << i):
            result |= (1 << (7 - i))
    return result

def mirrorHorizontal(pattern):
    """Mirror a pattern horizontally by reversing bits in each row."""
    return [reverseBits(byte) for byte in pattern]

def rotateLeft90(pattern):
    """Rotate pattern 90 degrees counter-clockwise (left)."""
    # Convert bytes to 8x8 bit array
    bits = []
    for byte in pattern:
        row = [(byte >> (7-i)) & 1 for i in range(8)]
        bits.append(row)
    
    # Rotate: new[row][col] = old[col][7-row]
    rotated = [[bits[col][7-row] for col in range(8)] for row in range(8)]
    
    # Convert back to bytes
    result = []
    for row in rotated:
        byte = 0
        for i, bit in enumerate(row):
            byte |= (bit << (7-i))
        result.append(byte)
    return result

# Image data from imageHexData.dat (raw values)
binarypic_raw = [241, 130, 132, 136, 240, 240, 240, 240]
sobelpic_raw = [96, 255, 127, 255, 255, 255, 255, 126]
cannypic_raw = [105, 81, 139, 80, 100, 73, 136, 41]

# Fix orientation: mirror horizontally then rotate left 90 degrees
binarypic = rotateLeft90(mirrorHorizontal(binarypic_raw))
sobelpic = rotateLeft90(mirrorHorizontal(sobelpic_raw))
cannypic = rotateLeft90(mirrorHorizontal(cannypic_raw))

# Letter patterns
letter_B = [0x00, 0x00, 0x7F, 0x49, 0x49, 0x36, 0x00, 0x00]  # "B"
letter_S_raw = [0x00, 0x00, 0x46, 0x49, 0x49, 0x31, 0x00, 0x00]  # "S" (mirrored)
letter_S = mirrorHorizontal(letter_S_raw)  # Fix horizontal mirror
letter_C = [0x00, 0x00, 0x3E, 0x41, 0x41, 0x22, 0x00, 0x00]  # "C"
blank = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]     # Blank screen

# Dictionary mapping labels to their data
data = {
    'B': letter_B,
    'binarypic': binarypic,
    'S': letter_S,
    'sobelpic': sobelpic,
    'C': letter_C,
    'cannypic': cannypic,
    'blank': blank
}
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

def displayPattern(pattern, duration):
    """Display a pattern for the specified duration in seconds."""
    start_time = time.time()
    while time.time() - start_time < duration:
        x = 0x80
        for i in range(0, 8):
            GPIO.output(latchPin, GPIO.LOW)
            shiftOut(dataPin, clockPin, MSBFIRST, pattern[i])
            shiftOut(dataPin, clockPin, MSBFIRST, ~x)
            GPIO.output(latchPin, GPIO.HIGH)
            time.sleep(0.001)
            x >>= 1

def loop():
    while True:
        # Display sequence: B (2s) -> binarypic (10s) -> blank (0.5s) -> S (2s) -> sobelpic (10s) -> blank (0.5s) -> C (2s) -> cannypic (10s) -> blank (0.5s)
        
        # Display B for 2 seconds
        displayPattern(data['B'], 2)
        # Display binarypic for 10 seconds
        displayPattern(data['binarypic'], 10)
        # Blank for 0.5 seconds
        displayPattern(data['blank'], 0.5)
        
        # Display S for 2 seconds
        displayPattern(data['S'], 2)
        # Display sobelpic for 10 seconds
        displayPattern(data['sobelpic'], 10)
        # Blank for 0.5 seconds
        displayPattern(data['blank'], 0.5)
        
        # Display C for 2 seconds
        displayPattern(data['C'], 2)
        # Display cannypic for 10 seconds
        displayPattern(data['cannypic'], 10)
        # Blank for 0.5 seconds
        displayPattern(data['blank'], 0.5)

def destroy():
    GPIO.cleanup()
if __name__ == '__main__':  # Program entrance
    print ('Program is starting...' )
    setup()
    try:
        loop()
    except KeyboardInterrupt:   # Press ctrl-c to end the program.
        destroy()
