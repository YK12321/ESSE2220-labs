import RPi.GPIO as GPIO
import logging
import time
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('led_display.log')
    ]
)

class LEDDisplayError(Exception):
    """Custom exception for LED Display operations"""
    pass

class LEDDisplay:
    """Production-ready LED Display controller for battery level indication"""
    
    # Configuration constants
    MIN_BATTERY = 0
    MAX_BATTERY = 100
    MIN_LEDS = 0
    MAX_LEDS = 10
    VALID_BCM_PINS = [2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 26]
    
    def __init__(self, batteryInput: float, ledPinsArrStatus: List[int], ledPinsArr: List[int]):
        """
        Initialize LED Display controller
        
        Args:
            batteryInput: Initial battery level (0-100)
            ledPinsArrStatus: Array to track LED states (should be same length as ledPinsArr)
            ledPinsArr: Array of GPIO pin numbers for LEDs
            
        Raises:
            LEDDisplayError: If initialization fails
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.gpio_initialized = False
        
        # Validate inputs
        self._validate_inputs(batteryInput, ledPinsArrStatus, ledPinsArr)
        
        self.batteryInput = batteryInput
        self.ledPinsArrStatus = ledPinsArrStatus
        self.ledPinsArr = ledPinsArr
        
        # Initialize GPIO
        self._initialize_gpio()
        
        self.logger.info(f"LEDDisplay initialized with {len(self.ledPinsArr)} LEDs on pins {self.ledPinsArr}")
    
    def _validate_inputs(self, batteryInput: float, ledPinsArrStatus: List[int], ledPinsArr: List[int]):
        """Validate all input parameters"""
        # Validate battery level
        if not (self.MIN_BATTERY <= batteryInput <= self.MAX_BATTERY):
            raise LEDDisplayError(f"Battery level must be between {self.MIN_BATTERY} and {self.MAX_BATTERY}")
        
        # Validate arrays have same length
        if len(ledPinsArrStatus) != len(ledPinsArr):
            raise LEDDisplayError("ledPinsArrStatus and ledPinsArr must have the same length")
        
        # Validate LED count
        if len(ledPinsArr) > self.MAX_LEDS:
            raise LEDDisplayError(f"Maximum {self.MAX_LEDS} LEDs supported")
        
        # Validate GPIO pins
        for pin in ledPinsArr:
            if pin not in self.VALID_BCM_PINS:
                raise LEDDisplayError(f"Invalid GPIO pin {pin}. Valid pins: {self.VALID_BCM_PINS}")
        
        # Check for duplicate pins
        if len(set(ledPinsArr)) != len(ledPinsArr):
            raise LEDDisplayError("Duplicate GPIO pins not allowed")
        
        self.logger.debug("Input validation completed successfully")
    
    def _initialize_gpio(self):
        """Initialize GPIO with error handling"""
        try:
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Set up all LED pins as outputs
            for pin in self.ledPinsArr:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)  # Start with all LEDs off
            
            self.gpio_initialized = True
            self.logger.info("GPIO initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            raise LEDDisplayError(f"GPIO initialization failed: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.cleanup()
        if exc_type:
            self.logger.error(f"Exception in context: {exc_type.__name__}: {exc_val}")
        return False
    
    def getCurrentBattery(self) -> float:
        """Get current battery level"""
        return self.batteryInput

    def mapValues(self, inputValues: float, minInput: float, maxInput: float, minOut: float, maxOut: float) -> float:
        """
        Map input values to output range with safety checks
        
        Args:
            inputValues: Value to map
            minInput: Minimum input value
            maxInput: Maximum input value  
            minOut: Minimum output value
            maxOut: Maximum output value
            
        Returns:
            Mapped value
            
        Raises:
            LEDDisplayError: If maxInput is zero or invalid range
        """
        if maxInput == 0:
            raise LEDDisplayError("maxInput cannot be zero")
        
        if maxInput <= minInput:
            raise LEDDisplayError("maxInput must be greater than minInput")
        
        # Clamp input to valid range
        inputValues = max(minInput, min(maxInput, inputValues))
        
        # Perform mapping
        mapped_value = ((inputValues - minInput) / (maxInput - minInput)) * (maxOut - minOut) + minOut
        
        # Clamp output to valid range
        return max(minOut, min(maxOut, mapped_value))

    def calculateLedStates(self):
        """Calculate which LEDs should be on based on battery level - all on at 100%, turn off from end as battery decreases"""
        try:
            ledsToEnable = int(self.mapValues(
                self.getCurrentBattery(), 
                self.MIN_BATTERY, 
                self.MAX_BATTERY, 
                self.MIN_LEDS, 
                len(self.ledPinsArrStatus)
            ))
            
            # Turn on LEDs from start of array up to ledsToEnable count
            # This means at 100% all LEDs are on, as battery decreases, LEDs turn off from the end
            for i in range(len(self.ledPinsArrStatus)):
                self.ledPinsArrStatus[i] = 1 if i < ledsToEnable else 0
            
            self.logger.debug(f"Calculated LED states: {ledsToEnable}/{len(self.ledPinsArrStatus)} LEDs enabled (from start of array)")
            
        except Exception as e:
            self.logger.error(f"Error calculating LED states: {e}")
            raise LEDDisplayError(f"Failed to calculate LED states: {e}")

    def setBatteryLevel(self, newLevel: float) -> float:
        """
        Update the battery level and trigger LED state calculation
        
        Args:
            newLevel: New battery level (0-100)
            
        Returns:
            The actual battery level set (clamped to valid range)
            
        Raises:
            LEDDisplayError: If update fails
        """
        try:
            # Validate and clamp battery level
            if not isinstance(newLevel, (int, float)):
                raise LEDDisplayError("Battery level must be a number")
            
            old_level = self.batteryInput
            self.batteryInput = max(self.MIN_BATTERY, min(self.MAX_BATTERY, newLevel))
            
            # Only recalculate if battery level actually changed
            if self.batteryInput != old_level:
                self.calculateLedStates()
                self.logger.info(f"Battery level updated: {old_level}% -> {self.batteryInput}%")
            
            return self.batteryInput
            
        except Exception as e:
            self.logger.error(f"Error setting battery level: {e}")
            raise LEDDisplayError(f"Failed to set battery level: {e}")

    def updateLedStates(self):
        """
        Update the actual GPIO pins to control the LEDs
        
        Raises:
            LEDDisplayError: If GPIO operations fail
        """
        if not self.gpio_initialized:
            raise LEDDisplayError("GPIO not initialized")
        
        try:
            # Count how many LEDs are on
            leds_on = sum(self.ledPinsArrStatus)
            
            # Log current state for development
            self.logger.info(f"Battery: {self.batteryInput}% | LEDs ON: {leds_on}/{len(self.ledPinsArrStatus)} | Pattern: {self.ledPinsArrStatus}")
            
            for i, pin in enumerate(self.ledPinsArr):
                if i < len(self.ledPinsArrStatus):
                    if self.ledPinsArrStatus[i] == 1:
                        GPIO.output(pin, GPIO.HIGH)  # Turn LED ON
                        self.logger.debug(f"LED {i+1} (Pin {pin}): ON")
                    else:
                        GPIO.output(pin, GPIO.LOW)   # Turn LED OFF
                        self.logger.debug(f"LED {i+1} (Pin {pin}): OFF")
                        
        except Exception as e:
            self.logger.error(f"Error updating LED states: {e}")
            raise LEDDisplayError(f"Failed to update LED states: {e}")
    
    def cleanup(self):
        """Clean up GPIO resources safely"""
        if self.gpio_initialized:
            try:
                # Turn off all LEDs before cleanup
                for pin in self.ledPinsArr:
                    GPIO.output(pin, GPIO.LOW)
                
                GPIO.cleanup()
                self.gpio_initialized = False
                self.logger.info("GPIO cleanup completed successfully")
                
            except Exception as e:
                self.logger.error(f"Error during GPIO cleanup: {e}")
        else:
            self.logger.debug("GPIO cleanup skipped - not initialized")
    
    def get_status(self) -> dict:
        """Get current status information for monitoring"""
        return {
            "battery_level": self.batteryInput,
            "led_states": self.ledPinsArrStatus.copy(),
            "led_pins": self.ledPinsArr.copy(),
            "leds_on": sum(self.ledPinsArrStatus),
            "gpio_initialized": self.gpio_initialized,
            "timestamp": time.time()
        }   