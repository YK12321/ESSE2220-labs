import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

# Morse code dictionary for alphanumeric characters
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '  '  # Space between words
}


# Define GPIO 26 pin for the LED
LED_PIN = 26
GPIO.setup(LED_PIN, GPIO.OUT)
# Data
studentNumbers = ["221116678", "221430194"]
unit = 0.2
shortDelay = 1*unit
longDelay = 3*unit
varDelay = 7*unit


def convertDataToMorse():
    morseArr = []
    for studentNumber in studentNumbers:
        morse_string = ""
        for char in studentNumber:
            if char.upper() in MORSE_CODE:
                morse_string += MORSE_CODE[char.upper()] + " "  # Add space between characters
        morseArr.append(morse_string.strip())  # Remove trailing space
    return morseArr

def pinOn(duration):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LED_PIN, GPIO.LOW)

def pinOff(duration):
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(duration)

def driveMorseToBlinks(morseInputArr):
    for morseInput in morseInputArr:
        for c in list(morseInput):
            if c == '.':
                pinOn(shortDelay)
            elif c == '-':
                pinOn(longDelay)
            elif c == ' ':
                pinOff(longDelay)
            pinOff(shortDelay)
    pinOff(varDelay)

def destroy():
    GPIO.cleanup()


if __name__ == '__main__':    # Program entrance
    try:
        driveMorseToBlinks(convertDataToMorse())
    except KeyboardInterrupt:   # Press ctrl-c to end the program.
        destroy()
