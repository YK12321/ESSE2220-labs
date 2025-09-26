import RPi.GPIO as GPIO
import time
from typing import List

class LEDDisplayError(Exception):
    pass

class LEDDisplay:
    MIN_BATTERY = 0
    MAX_BATTERY = 100
    MIN_LEDS = 0
    MAX_LEDS = 10
    VALID_BCM_PINS = [2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 26]
    
    def __init__(self, batteryInput: float, ledPinsArrStatus: List[int], ledPinsArr: List[int]):
        self._validate_inputs(batteryInput, ledPinsArrStatus, ledPinsArr)
        
        self.batteryInput = batteryInput
        self.ledPinsArrStatus = ledPinsArrStatus
        self.ledPinsArr = ledPinsArr
        self.gpio_initialized = False
        self.warning_active = False
        self.warning_start_time = 0
        self.warning_led_state = False
        self.original_led_states = None
        
        self._initialize_gpio()
    
    def _validate_inputs(self, batteryInput: float, ledPinsArrStatus: List[int], ledPinsArr: List[int]):
        if not (self.MIN_BATTERY <= batteryInput <= self.MAX_BATTERY):
            raise LEDDisplayError(f"Battery level must be between {self.MIN_BATTERY} and {self.MAX_BATTERY}")
        if len(ledPinsArrStatus) != len(ledPinsArr):
            raise LEDDisplayError("ledPinsArrStatus and ledPinsArr must have the same length")
        if len(ledPinsArr) > self.MAX_LEDS:
            raise LEDDisplayError(f"Maximum {self.MAX_LEDS} LEDs supported")
        for pin in ledPinsArr:
            if pin not in self.VALID_BCM_PINS:
                raise LEDDisplayError(f"Invalid GPIO pin {pin}")
        if len(set(ledPinsArr)) != len(ledPinsArr):
            raise LEDDisplayError("Duplicate GPIO pins not allowed")
    
    def _initialize_gpio(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            for pin in self.ledPinsArr:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            self.gpio_initialized = True
        except Exception as e:
            raise LEDDisplayError(f"GPIO initialization failed: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
    
    def getCurrentBattery(self) -> float:
        return self.batteryInput

    def mapValues(self, inputValues: float, minInput: float, maxInput: float, minOut: float, maxOut: float) -> float:
        if maxInput == 0 or maxInput <= minInput:
            raise LEDDisplayError("Invalid input range")
        inputValues = max(minInput, min(maxInput, inputValues))
        mapped_value = ((inputValues - minInput) / (maxInput - minInput)) * (maxOut - minOut) + minOut
        return max(minOut, min(maxOut, mapped_value))

    def calculateLedStates(self):
        try:
            if self.batteryInput == 0:
                ledsToEnable = 0
            else:
                ledsToEnable = max(1, int(self.mapValues(
                    self.getCurrentBattery(), 
                    self.MIN_BATTERY, 
                    self.MAX_BATTERY, 
                    self.MIN_LEDS, 
                    len(self.ledPinsArrStatus)
                )))
            
            for i in range(len(self.ledPinsArrStatus)):
                self.ledPinsArrStatus[i] = 1 if i < ledsToEnable else 0
                
        except Exception as e:
            raise LEDDisplayError(f"Failed to calculate LED states: {e}")

    def setBatteryLevel(self, newLevel: float) -> float:
        try:
            if not isinstance(newLevel, (int, float)):
                raise LEDDisplayError("Battery level must be a number")
            
            old_level = self.batteryInput
            self.batteryInput = max(self.MIN_BATTERY, min(self.MAX_BATTERY, newLevel))
            
            if self.batteryInput != old_level:
                self.calculateLedStates()
                if self.batteryInput <= 15 and old_level > 15:
                    self.triggerLowBatteryWarning()
            
            return self.batteryInput
            
        except Exception as e:
            raise LEDDisplayError(f"Failed to set battery level: {e}")

    def updateLedStates(self):
        if not self.gpio_initialized:
            raise LEDDisplayError("GPIO not initialized")
        
        try:
            self._update_warning_animation()
            
            if self.warning_active:
                return
            
            for i, pin in enumerate(self.ledPinsArr):
                if i < len(self.ledPinsArrStatus):
                    GPIO.output(pin, GPIO.HIGH if self.ledPinsArrStatus[i] == 0 else GPIO.LOW)
                        
        except Exception as e:
            raise LEDDisplayError(f"Failed to update LED states: {e}")
    
    def cleanup(self):
        if self.gpio_initialized:
            try:
                for pin in self.ledPinsArr:
                    GPIO.output(pin, GPIO.LOW)
                GPIO.cleanup()
                self.gpio_initialized = False
            except Exception:
                pass
    
    def triggerLowBatteryWarning(self):
        if not self.gpio_initialized or len(self.ledPinsArr) == 0 or self.warning_active:
            return
        
        try:
            self.original_led_states = self.ledPinsArrStatus.copy()
            self.warning_active = True
            self.warning_start_time = time.time()
            self.warning_led_state = False
        except Exception:
            pass

    def _update_warning_animation(self):
        if not self.warning_active:
            return
            
        try:
            elapsed_time = time.time() - self.warning_start_time
            flash_cycle_duration = 0.1
            time_in_cycle = elapsed_time % flash_cycle_duration
            leds_should_be_on = time_in_cycle < 0.05
            
            if leds_should_be_on != self.warning_led_state:
                self.warning_led_state = leds_should_be_on
                for pin in self.ledPinsArr:
                    GPIO.output(pin, GPIO.HIGH if leds_should_be_on else GPIO.LOW)
            
            if elapsed_time >= 0.3:
                self._end_warning_sequence()
        except Exception:
            self._end_warning_sequence()

    def _end_warning_sequence(self):
        try:
            self.warning_active = False
            self.warning_led_state = False
            
            if self.original_led_states is not None:
                self.ledPinsArrStatus = self.original_led_states.copy()
                self.original_led_states = None
            
            for i, pin in enumerate(self.ledPinsArr):
                if i < len(self.ledPinsArrStatus):
                    led_state = GPIO.LOW if self.ledPinsArrStatus[i] == 0 else GPIO.HIGH
                    GPIO.output(pin, led_state)
        except Exception:
            pass