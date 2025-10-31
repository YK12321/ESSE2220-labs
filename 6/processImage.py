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
    """Apply Sobel edge detection to the image."""
    # Use ksize=3 for small images (5 is too large for 8x8)
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
    sobel_combined = cv2.magnitude(sobelx, sobely)
    sobel_combined = np.uint8(np.clip(sobel_combined, 0, 255))
    return sobel_combined

def canny(image):
    """Apply Canny edge detection to the image."""
    edges = cv2.Canny(image, 100, 200)
    return edges

def convertToBinary(image, threshold=127, invert=False):
    """Convert a grayscale image to a binary image using the specified threshold.
    
    Args:
        image: Grayscale image
        threshold: Pixel values above this become 1 (white), below become 0 (black)
        invert: If True, invert the binary output (1 becomes 0, 0 becomes 1)
    """
    if invert:
        _, binary_image = cv2.threshold(image, threshold, 1, cv2.THRESH_BINARY_INV)
    else:
        _, binary_image = cv2.threshold(image, threshold, 1, cv2.THRESH_BINARY)
    return binary_image

def convertToHex(binary_image, reverse_bits=False):
    """Convert a binary image to hexadecimal representation for LED matrix.
    
    Args:
        binary_image: 8x8 binary image where 1=LED on, 0=LED off
        reverse_bits: If True, reverse the bit order in each row (MSB<->LSB)
    """
    hex_data = []
    print("\n=== Binary to Hex Conversion ===")
    for row_idx, row in enumerate(binary_image):
        # Ensure we only take 8 bits (8 pixels) per row
        row_flat = row.flatten() if len(row.shape) > 1 else row
        # Take only first 8 bits if row is longer
        row_8bit = row_flat[:8] if len(row_flat) > 8 else row_flat
        # Pad with zeros if row is shorter than 8 bits
        if len(row_8bit) < 8:
            row_8bit = np.pad(row_8bit, (0, 8 - len(row_8bit)), 'constant')
        
        # Reverse bits if needed (some LED matrices scan MSB first, others LSB first)
        if reverse_bits:
            row_8bit = row_8bit[::-1]
        
        bits = ''.join(str(int(bit)) for bit in row_8bit)
        # Convert to integer (removing the '0x' prefix issue)
        hex_value = int(bits, 2)
        hex_data.append(hex_value)
        print(f"Row {row_idx}: {bits} = {hex_value:3d} = 0x{hex_value:02x}")
    print("================================\n")
    return hex_data

if __name__ == '__main__':
    print('Program is starting...')
    try:
        image = loadImage("lab6_8x8_gray.png")
        #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = image #Image provided is already grayscale
        
        # FIRST: Resize to 8x8
        resized_8x8 = resizeImage(gray_image, (8, 8))
        
        # THEN: Apply edge detection on the 8x8 image
        sobel_8x8 = sobel(resized_8x8)
        canny_8x8 = canny(resized_8x8)
        
        # Choose which processed image to use for LED matrix
        processed_8x8 = sobel_8x8  # Change to canny_8x8 or resized_8x8 if desired
        
        # Create upscaled versions for better viewing (scale 8x8 to 240x240)
        scale_factor = 30
        original_large = cv2.resize(resized_8x8, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        sobel_large = cv2.resize(sobel_8x8, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        canny_large = cv2.resize(canny_8x8, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        processed_large = cv2.resize(processed_8x8, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        
        # Print pixel value ranges for debugging
        print("\n=== Pixel Value Ranges (for debugging) ===")
        print(f"Original 8x8:   min={resized_8x8.min()}, max={resized_8x8.max()}")
        print(f"Sobel 8x8:      min={sobel_8x8.min()}, max={sobel_8x8.max()}")
        print(f"Canny 8x8:      min={canny_8x8.min()}, max={canny_8x8.max()}")
        print(f"Processed 8x8:  min={processed_8x8.min()}, max={processed_8x8.max()}")
        
        # Convert all methods to binary for comparison
        # Set invert=True if you want dark pixels in image = LED on (common for displaying dark images on bright LEDs)
        invert_binary = True  # Change to False if LEDs should match white pixels in image
        
        binary_original = convertToBinary(resized_8x8, threshold=127, invert=invert_binary)
        binary_sobel = convertToBinary(sobel_8x8, threshold=127, invert=False)  # Edge detection typically doesn't need inversion
        binary_canny = convertToBinary(canny_8x8, threshold=127, invert=False)
        
        print(f"Binary original (inverted={invert_binary}): min={binary_original.min()}, max={binary_original.max()}")
        print(f"Binary sobel:    min={binary_sobel.min()}, max={binary_sobel.max()}")
        print(f"Binary canny:    min={binary_canny.min()}, max={binary_canny.max()}")
        
        # Print actual 8x8 binary pattern for original
        print("\n8x8 Binary Original Pattern (1=LED on, 0=LED off):")
        for row in binary_original:
            row_flat = row.flatten() if len(row.shape) > 1 else row
            print(''.join(str(int(pixel)) for pixel in row_flat))
        print("==========================================\n")
        
        # Create scaled versions for display
        binary_original_large = cv2.resize(binary_original * 255, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        binary_sobel_large = cv2.resize(binary_sobel * 255, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        binary_canny_large = cv2.resize(binary_canny * 255, (8 * scale_factor, 8 * scale_factor), interpolation=cv2.INTER_NEAREST)
        
        # Save all images to files
        cv2.imwrite("output_original_8x8.png", original_large)
        cv2.imwrite("output_sobel_8x8.png", sobel_large)
        cv2.imwrite("output_canny_8x8.png", canny_large)
        cv2.imwrite("output_binary_original.png", binary_original_large)
        cv2.imwrite("output_binary_sobel.png", binary_sobel_large)
        cv2.imwrite("output_binary_canny.png", binary_canny_large)
        
        print("Images saved (all scaled up 30x for viewing):")
        print("  - output_original_8x8.png (Original resized to 8x8)")
        print("  - output_sobel_8x8.png (Sobel edge detection on 8x8)")
        print("  - output_canny_8x8.png (Canny edge detection on 8x8)")
        print("  - output_binary_original.png (Binary of original)")
        print("  - output_binary_sobel.png (Binary of Sobel - for LED)")
        print("  - output_binary_canny.png (Binary of Canny - for LED)")
        
        # Display images in windows
        cv2.imshow("1. Original 8x8", original_large)
        cv2.imshow("2. Sobel 8x8", sobel_large)
        cv2.imshow("3. Canny 8x8", canny_large)
        cv2.imshow("4. Binary Original", binary_original_large)
        cv2.imshow("5. Binary Sobel", binary_sobel_large)
        cv2.imshow("6. Binary Canny", binary_canny_large)
        
        # Convert all to hex data
        # Try reverse_bits=True if the LED display is mirrored horizontally
        reverse_bits = False  # Change to True if display is horizontally flipped
        
        print("\n--- Converting BINARY to hex ---")
        hex_binary = convertToHex(binary_original, reverse_bits)
        print("\n--- Converting SOBEL to hex ---")
        hex_sobel = convertToHex(binary_sobel, reverse_bits)
        print("\n--- Converting CANNY to hex ---")
        hex_canny = convertToHex(binary_canny, reverse_bits)
        
        # Display in format compatible with ledMatrix.py
        print("\nHexadecimal representation for LED Matrix:")
        print(f"binarypic = {hex_binary}")
        print(f"sobelpic = {hex_sobel}")
        print(f"cannypic = {hex_canny}")

        # Also save to file
        with open("imageHexData.dat", "w") as f:
            f.write(f"binarypic = {hex_binary}\n")
            f.write(f"sobelpic = {hex_sobel}\n")
            f.write(f"cannypic = {hex_canny}\n")
        
        print("\nData saved to imageHexData.dat")
        print(f"Number of rows: {len(hex_sobel)}")
        
        # Wait for key press to close windows
        print("\nPress any key in the image window to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f'Error: {e}')