import cv2
import numpy as np

def loadImage(path):
    """Load an image from the specified file path."""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {path}")
    return image

def resizeImage(image, size=(8, 8)):
    """Resize image to specified dimensions (default 8x8 for LED matrix)."""
    resized = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    return resized

def sobel(image):
    pass  # Placeholder for Sobel function if needed later

def canny(image):
    pass  # Placeholder for Canny function if needed later

def convertToBinary(image, threshold=127):
    """Convert a grayscale image to a binary image using the specified threshold."""
    _, binary_image = cv2.threshold(image, threshold, 1, cv2.THRESH_BINARY)
    return binary_image

def convertToHex(binary_image):
    """Convert a binary image to hexadecimal representation for LED matrix."""
    hex_data = []
    for row in binary_image:
        # Ensure we only take 8 bits (8 pixels) per row
        row_flat = row.flatten() if len(row.shape) > 1 else row
        # Take only first 8 bits if row is longer
        row_8bit = row_flat[:8] if len(row_flat) > 8 else row_flat
        # Pad with zeros if row is shorter than 8 bits
        if len(row_8bit) < 8:
            row_8bit = np.pad(row_8bit, (0, 8 - len(row_8bit)), 'constant')
        bits = ''.join(str(int(bit)) for bit in row_8bit)
        # Convert to integer (removing the '0x' prefix issue)
        hex_value = int(bits, 2)
        hex_data.append(hex_value)
    return hex_data

if __name__ == '__main__':
    print('Program is starting...')
    try:
        image = loadImage("lab6_8x8_gray.png")
        #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = image #Image provided is already grayscale
        
        # Resize to 8x8 if needed
        resized_image = resizeImage(gray_image, (8, 8))
        
        binary_image = convertToBinary(resized_image)
        hex_data = convertToHex(binary_image)
        
        # Display in format compatible with ledMatrix.py
        print("Hexadecimal representation for LED Matrix:")
        print(f"pic = {hex_data}")
        
        # Also save to file
        with open("imageHexData.dat", "w") as f:
            f.write(f"pic = {hex_data}\n")
        
        print("\nData saved to imageHexData.dat")
        print(f"Number of rows: {len(hex_data)}")

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f'Error: {e}')