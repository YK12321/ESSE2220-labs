import RPi.GPIO as GPIO #type: ignore
import time
GPIO.setmode(GPIO.BCM)

# Global Variables / Data
studentNumbers = ["221116678", "221430194"]
unit = 0.2
shortDelay = 1*unit
longDelay = 3*unit
varDelay = 7*unit
LED_PIN = 26  # Define LED pin globally

# Morse code dictionary for alphanumeric characters (uses map and key concept from Java course)
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

"""Setup function to configure GPIO pins"""
def setup():
    # Configure the LED pin as output
    GPIO.setup(LED_PIN, GPIO.OUT)

"""Convert student numbers to Morse code"""
def convertDataToMorse():
    morseArr = []
    for studentNumber in studentNumbers:
        morse_string = ""
        for char in studentNumber:
            if char.upper() in MORSE_CODE:
                morse_string += MORSE_CODE[char.upper()] + " "  # Add space between characters
        morseArr.append(morse_string.strip())  # Remove trailing space
    return morseArr

"""Functions to control the LED pin"""
def pinOn(duration):
    GPIO.output(LED_PIN, GPIO.HIGH) #type: ignore
    time.sleep(duration)
    GPIO.output(LED_PIN, GPIO.LOW) #type: ignore

"""Turn off the pin for a specified duration"""
def pinOff(duration):
    GPIO.output(LED_PIN, GPIO.LOW) # type: ignore
    time.sleep(duration)

"""Drive the Morse code to blinks on the LED"""
def driveMorseToBlinks(morseInputArr):
    for i, morseInput in enumerate(morseInputArr):
        print(f"Playing student number {i+1}: {studentNumbers[i]} -> {morseInput}")
        for c in list(morseInput):
            if c == '.':
                pinOn(shortDelay)
                pinOff(shortDelay)  # Short delay after dot
            elif c == '-':
                pinOn(longDelay)
                pinOff(shortDelay)  # Short delay after dash
            elif c == ' ':
                pinOff(longDelay)  # Space between characters (no additional delay needed)
        
        # Add delay between different student numbers
        if i < len(morseInputArr):
            print("Delay between student numbers...")
            pinOff(varDelay)

def destroy():
    GPIO.cleanup()


if __name__ == '__main__':    # Program entrance
    setup()
    try:
        while True:
            driveMorseToBlinks(convertDataToMorse())
    except KeyboardInterrupt:   # Handle Ctrl+C gracefully
        print("\nProgram interrupted by user")
    except Exception as e:   # Handle other exceptions
        print(f"An error occurred: {e}")
    finally:
        destroy()
