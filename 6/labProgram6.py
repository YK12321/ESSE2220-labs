import cv2
import numpy as np
from ledClass import LEDPanel

def loadImage(path):
    """Load an image from the specified file path."""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {path}")
    return image

def displayImageOnLed(image, led_panel):
    """Display a grayscale image on the LED panel."""
    if image.shape[0] == 8 and image.shape[1] == 8:
        resized_image = image
    else:
        # Resize image to 8x8
        resized_image = cv2.resize(image, (8, 8), interpolation=cv2.INTER_AREA)
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    
    # Threshold to get binary image
    _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)
    
    # Prepare pattern data for LED panel
    pattern_data = []
    for row in binary_image:
        byte = 0
        for i, pixel in enumerate(row):
            if pixel > 0:  # White pixel
                byte |= (1 << (7 - i))
        pattern_data.append(byte)
    
    # Display the pattern on the LED panel
    led_panel.display_custom_pattern(pattern_data, duration=0.005, repeat=100)

def main():
    image = loadImage("lab6_8x8_gray.png")
    with LEDPanel() as led_panel:
        displayImageOnLed(image, led_panel)

if __name__ == '__main__':
    print('Program is starting...')
    try:
        main()
    except KeyboardInterrupt:
        print('\nProgram stopped by user')
    except Exception as e:
        print(f'Error: {e}')