"""
Lab 4 - Joystick ADC Interface
ESSE 2220
Reads joystick position using ADS7830 ADC module via I2C
"""

import RPi.GPIO as GPIO
import numpy as np
import smbus
import time

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================
Z_PIN = 18          # GPIO pin for joystick Z-axis (button)
SDA_PIN = 2         # GPIO pin for I2C SDA
SCL_PIN = 3         # GPIO pin for I2C SCL

# ============================================================================
# I2C CONFIGURATION
# ============================================================================
ADC_ADDRESS = 0x4b  # I2C address for ADS7830 ADC module
ADC_CMD = 0x84      # Command byte for ADS7830

# ============================================================================
# ADC DEVICE CLASSES
# ============================================================================
class ADCDevice(object):
    """Base class for ADC devices with I2C communication"""
    
    def __init__(self):
        """Initialize I2C bus communication"""
        self.bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1


class ADS7830(ADCDevice):
    """ADS7830 8-channel 8-bit ADC module"""
    
    def __init__(self, address=ADC_ADDRESS):
        """
        Initialize ADS7830 ADC
        
        Args:
            address: I2C address (default: 0x4b)
        """
        super(ADS7830, self).__init__()
        self.cmd = ADC_CMD
        self.address = address
        
    def analogRead(self, channel):
        """
        Read analog value from specified ADC channel
        
        Args:
            channel: ADC input channel (0-7)
            
        Returns:
            int: Analog reading (0-255)
        """
        if not 0 <= channel <= 7:
            raise ValueError("Channel must be between 0 and 7")
            
        # Calculate channel command byte
        channel_cmd = self.cmd | (((channel << 2 | channel >> 1) & 0x07) << 4)
        value = self.bus.read_byte_data(self.address, channel_cmd)
        return value

# ============================================================================
# SETUP AND UTILITY FUNCTIONS
# ============================================================================
def setup():
    """
    Initialize GPIO pins and ADC device
    
    Returns:
        ADS7830: Initialized ADC object
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Z_PIN, GPIO.IN)
    adc = ADS7830()
    return adc


def detectI2C(adc, addr):
    """
    Detect if I2C device exists at specified address
    
    Args:
        adc: ADC device object
        addr: I2C address to check
        
    Returns:
        bool: True if device found, False otherwise
    """
    try:
        adc.bus.write_byte(addr, 0)
        print(f"Found device at address 0x{addr:02x}")
        return True
    except Exception as e:
        print(f"No device found at address 0x{addr:02x}")
        return False


def getUserInput():
    """
    Prompt user for initial and final coordinates
    
    Returns:
        numpy.ndarray: 2x2 array of [initial, final] coordinates
    """
    print("\n=== Coordinate Input ===")
    
    # Get initial coordinates
    init_x = float(input("Enter initial x coordinate: "))
    init_y = float(input("Enter initial y coordinate: "))
    initialCoords = [init_x, init_y]
    
    # Get final coordinates
    final_x = float(input("Enter final x coordinate: "))
    final_y = float(input("Enter final y coordinate: "))
    finalCoords = [final_x, final_y]
    
    return np.array([initialCoords, finalCoords])


def readRawJoystickPosition(adc):
    """
    Read current joystick X and Y position from ADC
    
    Args:
        adc: ADS7830 ADC object
        
    Returns:
        tuple: (x_value, y_value) as integers (0-255)
    """
    x_value = adc.analogRead(0)  # Channel 0 for X-axis
    y_value = adc.analogRead(1)  # Channel 1 for Y-axis
    return x_value, y_value

def fixRawToCalibrated(x_raw, y_raw, center, scale, tol, deadZone = .1):
    # Apply dead zone
    if abs((x_raw - center)/127 * scale) < deadZone:
        x_raw = center
    if abs((y_raw - center)/127 * scale) < deadZone:
        y_raw = center
    nx = ((x_raw-center)/127) * scale
    ny = ((y_raw-center)/127) * scale
    return np.array([nx, ny])


def updatePosition(currentPos, delta, isBoostEnabled, boostFactor):
    if isBoostEnabled:
        delta *= boostFactor
    newPos = currentPos + delta
    return newPos

def comparePositions(pos1, pos2, tol):
    return np.all(np.abs(pos1 - pos2) <= tol)

# ============================================================================
# MAIN PROGRAM
# ============================================================================
def main():
    """Main program execution"""
    # Initialize hardware
    adc = setup()
    
    # Get user input for coordinates
    coords = getUserInput()
    initialPos = coords[0]
    finalPos = coords[1]
    
    # Display coordinate information
    print("\n=== Coordinate Summary ===")
    print(f"Initial Coordinates: {initialPos}")
    print(f"Final Coordinates: {finalPos}")
    
    # Read and display initial joystick position
    x_pos, y_pos = readRawJoystickPosition(adc)
    print(f"\n=== Initial Joystick Position ===")
    print(f"X: {x_pos}, Y: {y_pos}")
    print(f"Raw: ({x_pos}, {y_pos})")
    CENTER = 128
    SCALE = 1
    TOL = .5
    boostFactor = 1.5
    print(f"Calibrated: ({fixRawToCalibrated(x_pos, y_pos, CENTER, SCALE, TOL)})")

    reachedTarget = False
    if(comparePositions(initialPos, finalPos, TOL)):
        reachedTarget = True
        print("Initial position is the same as final position. No movement needed.")
    else:
        while not reachedTarget:
            x_pos, y_pos = readRawJoystickPosition(adc)
            calibratedPos = fixRawToCalibrated(x_pos, y_pos, CENTER, SCALE, TOL)
            print(f"\nCurrent Joystick Position: {calibratedPos}")
            
            # Update current position based on joystick input
            isBoostEnabled = GPIO.input(Z_PIN) == GPIO.LOW
            initialPos = updatePosition(initialPos, calibratedPos, isBoostEnabled, boostFactor)
            print(f"Updated Position: {initialPos}")
            if isBoostEnabled:
                print("Boost Enabled on this movement!")
            
            # Check if target is reached within tolerance
            if np.all(np.abs(initialPos - finalPos) <= TOL):
                reachedTarget = True
                print("Reached target position!")
            
            time.sleep(0.5)  # Delay for readability




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")