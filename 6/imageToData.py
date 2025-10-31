import cv2
import numpy as np

def loadImage(path):
    """Load an image from the specified file path."""
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {path}")
    return image

def downscaleToOriginal(image, target_size=(8, 8)):
    """Downscale the upscaled image back to original 8x8 size."""
    # Use INTER_NEAREST to preserve the binary values
    downscaled = cv2.resize(image, target_size, interpolation=cv2.INTER_NEAREST)
    return downscaled

def convertToBinary(image, threshold=127):
    """Convert grayscale image to binary (0 or 1)."""
    # Threshold the image: values > threshold become 1, else 0
    _, binary_image = cv2.threshold(image, threshold, 1, cv2.THRESH_BINARY)
    return binary_image

def convertToHex(binary_image):
    """Convert binary image to hexadecimal representation for LED matrix."""
    hex_data = []
    print("\n=== Binary to Hex Conversion ===")
    for row_idx, row in enumerate(binary_image):
        # Flatten the row if needed
        row_flat = row.flatten() if len(row.shape) > 1 else row
        # Take only first 8 bits (should already be 8x8)
        row_8bit = row_flat[:8] if len(row_flat) > 8 else row_flat
        # Pad with zeros if row is shorter than 8 bits
        if len(row_8bit) < 8:
            row_8bit = np.pad(row_8bit, (0, 8 - len(row_8bit)), 'constant')
        
        bits = ''.join(str(int(bit)) for bit in row_8bit)
        hex_value = int(bits, 2)
        hex_data.append(hex_value)
        print(f"Row {row_idx}: {bits} = {hex_value:3d} = 0x{hex_value:02x}")
    print("================================\n")
    return hex_data

if __name__ == '__main__':
    print('Image to Data Converter - Starting...\n')
    
    try:
        # List of images to process
        images_to_process = [
            ('output_binary_original.png', 'binarypic'),
            ('output_binary_sobel.png', 'sobelpic'),
            ('output_binary_canny.png', 'cannypic')
        ]
        
        results = {}
        
        for image_path, var_name in images_to_process:
            print(f"Processing {image_path}...")
            try:
                # Load the image
                image = loadImage(image_path)
                print(f"  Loaded: {image.shape[1]}x{image.shape[0]} pixels")
                
                # Downscale to 8x8 if needed
                if image.shape != (8, 8):
                    image_8x8 = downscaleToOriginal(image, (8, 8))
                    print(f"  Downscaled to: 8x8")
                else:
                    image_8x8 = image
                
                # Convert to binary
                binary_image = convertToBinary(image_8x8)
                
                # Convert to hex
                print(f"  Converting to hex data for '{var_name}':")
                hex_data = convertToHex(binary_image)
                
                results[var_name] = hex_data
                print(f"  ✓ {var_name} = {hex_data}\n")
                
            except FileNotFoundError:
                print(f"  ✗ File not found: {image_path}, skipping...\n")
                continue
        
        # Write to imageData.log
        with open("imageData.log", "w") as f:
            f.write("# Image Data for LED Matrix\n")
            f.write("# Generated from binary output images\n\n")
            
            for var_name, hex_data in results.items():
                f.write(f"{var_name} = {hex_data}\n")
        
        print(f"\n✓ Data saved to imageData.log")
        print(f"✓ Processed {len(results)} images successfully")
        
        # Display summary
        print("\n=== Summary ===")
        for var_name, hex_data in results.items():
            print(f"{var_name} = {hex_data}")
        
    except Exception as e:
        print(f'Error: {e}')
