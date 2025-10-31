import RPi.GPIO as GPIO
import time


class LEDPanel:
    """
    A class to control an 8x8 LED matrix using 74HC595 shift registers.
    Provides easy-to-use functions for displaying patterns, text, and animations.
    """
    
    # Shift register order constants
    LSBFIRST = 1
    MSBFIRST = 2
    
    # Pre-defined patterns
    SMILING_FACE = [0x1c, 0x22, 0x51, 0x45, 0x45, 0x51, 0x22, 0x1c]
    
    # Character data for "0-F" (8 bytes per character)
    CHAR_DATA = {
        ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        '0': [0x00, 0x00, 0x3E, 0x41, 0x41, 0x3E, 0x00, 0x00],
        '1': [0x00, 0x00, 0x21, 0x7F, 0x01, 0x00, 0x00, 0x00],
        '2': [0x00, 0x00, 0x23, 0x45, 0x49, 0x31, 0x00, 0x00],
        '3': [0x00, 0x00, 0x22, 0x49, 0x49, 0x36, 0x00, 0x00],
        '4': [0x00, 0x00, 0x0E, 0x32, 0x7F, 0x02, 0x00, 0x00],
        '5': [0x00, 0x00, 0x79, 0x49, 0x49, 0x46, 0x00, 0x00],
        '6': [0x00, 0x00, 0x3E, 0x49, 0x49, 0x26, 0x00, 0x00],
        '7': [0x00, 0x00, 0x60, 0x47, 0x48, 0x70, 0x00, 0x00],
        '8': [0x00, 0x00, 0x36, 0x49, 0x49, 0x36, 0x00, 0x00],
        '9': [0x00, 0x00, 0x32, 0x49, 0x49, 0x3E, 0x00, 0x00],
        'A': [0x00, 0x00, 0x3F, 0x44, 0x44, 0x3F, 0x00, 0x00],
        'B': [0x00, 0x00, 0x7F, 0x49, 0x49, 0x36, 0x00, 0x00],
        'C': [0x00, 0x00, 0x3E, 0x41, 0x41, 0x22, 0x00, 0x00],
        'D': [0x00, 0x00, 0x7F, 0x41, 0x41, 0x3E, 0x00, 0x00],
        'E': [0x00, 0x00, 0x7F, 0x49, 0x49, 0x41, 0x00, 0x00],
        'F': [0x00, 0x00, 0x7F, 0x48, 0x48, 0x40, 0x00, 0x00],
    }
    
    def __init__(self, data_pin=11, latch_pin=13, clock_pin=15):
        """
        Initialize the LED panel with specified GPIO pins.
        
        Args:
            data_pin: DS Pin of 74HC595 (Pin 14)
            latch_pin: ST_CP Pin of 74HC595 (Pin 12)
            clock_pin: SH_CP Pin of 74HC595 (Pin 11)
        """
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Configure GPIO pins for the LED panel."""
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.latch_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)
    
    def _shift_out(self, order, value):
        """
        Shift out a byte of data to the shift register.
        
        Args:
            order: LSBFIRST or MSBFIRST
            value: Byte value to shift out
        """
        for i in range(8):
            GPIO.output(self.clock_pin, GPIO.LOW)
            if order == self.LSBFIRST:
                GPIO.output(self.data_pin, (0x01 & (value >> i) == 0x01) and GPIO.HIGH or GPIO.LOW)
            elif order == self.MSBFIRST:
                GPIO.output(self.data_pin, (0x80 & (value << i) == 0x80) and GPIO.HIGH or GPIO.LOW)
            GPIO.output(self.clock_pin, GPIO.HIGH)
    
    def display_pattern(self, pattern, duration=0.001, repeat=1):
        """
        Display an 8-byte pattern on the LED matrix.
        
        Args:
            pattern: List of 8 bytes representing the pattern
            duration: Time to display each column (default 0.001s)
            repeat: Number of times to repeat the pattern (default 1)
        """
        for _ in range(repeat):
            x = 0x80
            for i in range(8):
                GPIO.output(self.latch_pin, GPIO.LOW)
                self._shift_out(self.MSBFIRST, pattern[i])
                self._shift_out(self.MSBFIRST, ~x)
                GPIO.output(self.latch_pin, GPIO.HIGH)
                time.sleep(duration)
                x >>= 1
    
    def display_text(self, text, frame_duration=0.001, frame_repeats=20):
        """
        Display scrolling text on the LED matrix.
        
        Args:
            text: String of characters to display (supports 0-9, A-F, space)
            frame_duration: Time to display each column (default 0.001s)
            frame_repeats: Times to repeat each frame (default 20)
        """
        # Convert text to data array
        data = []
        for char in text.upper():
            if char in self.CHAR_DATA:
                data.extend(self.CHAR_DATA[char])
        
        # Scroll through the text
        for k in range(len(data) - 8):
            for _ in range(frame_repeats):
                x = 0x80
                for i in range(k, k + 8):
                    GPIO.output(self.latch_pin, GPIO.LOW)
                    self._shift_out(self.MSBFIRST, data[i])
                    self._shift_out(self.MSBFIRST, ~x)
                    GPIO.output(self.latch_pin, GPIO.HIGH)
                    time.sleep(frame_duration)
                    x >>= 1
    
    def display_character(self, char, duration=0.001, repeat=100):
        """
        Display a single character on the LED matrix.
        
        Args:
            char: Character to display (supports 0-9, A-F, space)
            duration: Time to display each column (default 0.001s)
            repeat: Number of times to repeat (default 100)
        """
        char = char.upper()
        if char in self.CHAR_DATA:
            self.display_pattern(self.CHAR_DATA[char], duration, repeat)
    
    def display_smiling_face(self, duration=0.001, repeat=500):
        """
        Display a smiling face pattern.
        
        Args:
            duration: Time to display each column (default 0.001s)
            repeat: Number of times to repeat (default 500)
        """
        self.display_pattern(self.SMILING_FACE, duration, repeat)
    
    def clear(self):
        """Clear the LED panel."""
        self.display_pattern([0x00] * 8, duration=0.001, repeat=1)
    
    def display_custom_pattern(self, pattern_data, duration=0.001, repeat=1):
        """
        Display a custom pattern defined by raw byte data.
        
        Args:
            pattern_data: List of bytes representing the pattern
            duration: Time to display each column (default 0.001s)
            repeat: Number of times to repeat (default 1)
        """
        self.display_pattern(pattern_data, duration, repeat)
    
    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup GPIO."""
        self.cleanup()



