import RPi.GPIO as GPIO
import planet_tones
import time
import math

buzzerPin = 13        # define the buzzerPin
buttonPin = 18        # define the buttonPin
planetObject = None

def setup():
    global p
    GPIO.setmode(GPIO.BCM)          # Use PHYSICAL GPIO Numbering
    GPIO.setup(buzzerPin, GPIO.OUT) # set RGBLED pins to OUTPUT mode
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set buttonPin to INPUT mode, and pull up to 
    p = GPIO.PWM(buzzerPin, 1)
    p.start(0)

def stopAlerter():
    p.stop()

def loop():
    while True:
        if GPIO.input(buttonPin) == GPIO.LOW:
            alertor()
            print('alertor turned on >>>')
        else:
            stopAlerter()
            print('alertor turned off <<<')

def alertor():
    p.start(50)
    for x in range(0, 361):  # sweep through a sine wave
        # toneVal = 2000 + sinVal * 500  # frequency swings up and down
        trigVar = "sin"  # change to "tan" or "cos" to try other waveforms
        coefficient = 5
        degree = 0.5
        if(trigVar == "sin"):
            sinVal = math.sin(coefficient * math.pow((x * (math.pi / 180.0)), degree))
            toneVal = planetObject.getCalculatedTone(sinVal)
        elif(trigVar == "tan"):
            tanVal = math.tan(coefficient * math.pow((x * (math.pi / 180.0)), degree))
            toneVal = planetObject.getCalculatedTone(tanVal)
        elif(trigVar == "cos"):
            cosVal = math.cos(coefficient * math.pow((x * (math.pi / 180.0)), degree))
            toneVal = planetObject.getCalculatedTone(cosVal)
        p.ChangeFrequency(toneVal)
        time.sleep(0.001)


def destroy():
    GPIO.output(buzzerPin, GPIO.LOW)     # Turn off buzzer
    GPIO.cleanup()                       # Release GPIO resource
if __name__ == '__main__':               # Program entrance
    print('Program is starting...')
    planet = input("Enter a planet (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune): ").strip().lower()
    planet_classes = {
        "mercury": planet_tones.Mercury,
        "venus": planet_tones.Venus,
        "earth": planet_tones.Earth,
        "mars": planet_tones.Mars,
        "jupiter": planet_tones.Jupiter,
        "saturn": planet_tones.Saturn,
        "uranus": planet_tones.Uranus,
        "neptune": planet_tones.Neptune
    }
    # Initialize the selected planet
    if planet in planet_classes:
        selected_planet = planet_classes[planet]()
        base, depth = selected_planet.get_tone()
        planetObject = selected_planet
        print(f"Selected Planet: {selected_planet.name}, Base Frequency: {base} Hz, Depth: {depth} Hz")
    else:
        print("Invalid planet name. Please choose from the list.")
        exit(1)

    setup()
    try:
        loop()
    except KeyboardInterrupt:            # Press ctrl-c to end the program.
        destroy()