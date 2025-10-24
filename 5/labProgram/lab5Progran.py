#!/usr/bin/env python3
########################################################################
# Filename    : UltrasonicRanging.py
# Description : Get distance via UltrasonicRanging sensor
# auther      : www.freenove.com
# modification: 2019/12/28
########################################################################
import RPi.GPIO as GPIO
import time
import csv

trigPin = 16
echoPin = 18
MAX_DISTANCE = 220          # define the maximum measuring distance, unit: cm
timeOut = MAX_DISTANCE*60   # calculate timeout according to the maximum measuring distance
fileName = "distance_log.txt"
csvFileName = "distance_log.csv"

def writeToLog(sensorReading, time, iteration):
    # Use try-except to avoid program crash
    try:
        # Write to text file
        with open(fileName, "a") as f:
            if(iteration == 1):
                f.write("time_s    distance_cm\n")
            f.write(f"{time:.3f}    {sensorReading:.2f}\n")
        # Also write to CSV file
        with open(csvFileName, "a", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            if(iteration == 1):
                csvwriter.writerow(["time_s", "distance_cm"])
            csvwriter.writerow([f"{time:.3f}", f"{sensorReading:.2f}"])
        return 1
    except:
        return 0

def pulseIn(pin,level,timeOut): # obtain pulse time of a pin under timeOut
    t0 = time.time()
    while(GPIO.input(pin) != level):
        if((time.time() - t0) > timeOut*0.000001):
            return 0
    t0 = time.time()
    while(GPIO.input(pin) == level):
        if((time.time() - t0) > timeOut*0.000001):
            return 0
    pulseTime = (time.time() - t0)*1000000
    return pulseTime
    
def getSonar():     # get the measurement results of ultrasonic module,with unit: cm
    GPIO.output(trigPin,GPIO.HIGH)      # make trigPin output 10us HIGH level 
    time.sleep(0.00001)     # 10us
    GPIO.output(trigPin,GPIO.LOW) # make trigPin output LOW level 
    pingTime = pulseIn(echoPin,GPIO.HIGH,timeOut)   # read plus time of echoPin
    distance = pingTime * 340.0 / 2.0 / 10000.0     # calculate distance with sound speed 340m/s 
    return distance
    
def setup():
    GPIO.setmode(GPIO.BOARD)      # use PHYSICAL GPIO Numbering
    GPIO.setup(trigPin, GPIO.OUT)   # set trigPin to OUTPUT mode
    GPIO.setup(echoPin, GPIO.IN)    # set echoPin to INPUT mode

def loop():
    # Start with iteration 1
    iteration = 1

    # Clear previous log files / create new ones at the start
    with open(fileName, "w") as f:
        f.write("")  # clear the log file at the start
    with open(csvFileName, "w", newline='') as csvfile:
        csvfile.write("")  # clear the CSV log file at the start

    while(True):
        distance = getSonar() # get distance
        time.sleep(0.1)
        writeToLog(distance, iteration*0.1, iteration)
        iteration = iteration + 1
        
if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        GPIO.cleanup()         # release GPIO resource