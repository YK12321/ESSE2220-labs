"""
Lab 7: Feature Detection in Space Images (SIFT & ORB)
-----------------------------------------------------
Instructions:
1. Fill in the missing parts using the OpenCV documentation.
2. You must look up how to use the functions marked with TODO.
3. Use the official docs: https://docs.opencv.org/
   or Google search like: cv2.SIFT_create site:docs.opencv.org
4. Save all your output images using cv2.imwrite().
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- Step 1: Read the image ---
img = cv2.imread('space.jpg', cv2.IMREAD_GRAYSCALE)

# TODO: Try IMREAD_COLOR instead.
img_color = cv2.imread('space.jpg', cv2.IMREAD_COLOR)
# Then print img.shape for both cases and describe what changes.
print("Grayscale image shape:", img.shape)
print("Color image shape:", img_color.shape)
# What does the shape tell you about the number of channels (grayscale vs color)?
# Example: print(img.shape)
"""Grayscale image has two dimensions (height, width), whereas
the Color image has three dimensions (height, width, 3(we can hypothesize number of color channels (i.e. RGB)))"""


# --- Step 2: Create SIFT detector ---
# TODO: Find how to create a SIFT detector object in the docs.
sift = cv2.SIFT_create()

# --- Step 3: Detect keypoints and descriptors ---
# TODO: Look up how to detect and compute both at once.
keypoints_sift, descriptors_sift = sift.detectAndCompute(img, None)

# --- Step 4: Print some info ---
print("Number of keypoints (SIFT):", len(keypoints_sift))
print("Descriptor shape (SIFT):", descriptors_sift.shape)

# --- Step 5: Draw SIFT keypoints ---
# TODO: Look up drawKeypoints function in docs.
# Search what flags can be used (hint: something about “rich keypoints”).
# Design your own color for SIFT visualization using an RGB tuple, e.g., (R, G, B).
# Write in your report what color it represents and how you designed it.
img_sift = cv2.drawKeypoints(img, keypoints_sift, None, (255, 0, 255))
"""This color was picked because the bright magenta color rarely occurs in raw
starfield imagery, and is easily distinguishable from the dark background, and is 
not cofused with common blue/red nebulas"""

# Save the output image.
cv2.imwrite('sift_keypoints.jpg', img_sift)

# --- Step 6: Create ORB detector ---
# TODO: Find ORB_create and its parameters (e.g., nfeatures).
# Hint: A common starting value is around 500, but try different values (like 100, 1000)
# and describe how changing this number affects the number of detected keypoints.
orb = cv2.ORB_create(nfeatures=500)

# --- Step 7: Detect and compute with ORB ---
keypoints_orb, descriptors_orb = orb.detectAndCompute(img, None)

print("Number of keypoints (ORB):", len(keypoints_orb))
print("Descriptor shape (ORB):", descriptors_orb.shape)

# --- Step 8: Draw ORB keypoints ---
# TODO: Draw keypoints using a different RGB color than SIFT.
# You must also add appropriate flags for drawing.
# Explain what color you chose and why.
img_orb = cv2.drawKeypoints(img, keypoints_orb, None, (255, 0, 255))
cv2.imwrite('orb_keypoints.jpg', img_orb)

# --- Step 9: Top 50 strongest keypoints ---
# TODO: Use the Python function "sorted" to sort keypoints by their response value.
# You must Google what sorted() does and how to use the "key" parameter.
# "response" measures how strong or distinctive a detected feature is — higher = stronger feature.
# Then select the top 50 keypoints for both SIFT and ORB and visualize them.
# Save the resulting images as 'sift_top50.jpg' and 'orb_top50.jpg'.
def getResponse(kp):
    return kp.response

sorted_sift = sorted(keypoints_sift, key=getResponse, reverse=True)
sorted_orb = sorted(keypoints_orb, key=getResponse, reverse=True)

sorted_sift = sorted_sift[:50]
sorted_orb = sorted_orb[:50]

#for i, (kps, kpo) in enumerate(zip(sorted_sift, sorted_orb)):
#    print(i, kps.response, kpo.response)


print("Top 50 SIFT keypoints responses:", len(sorted_sift))

cv2.imwrite("sift_top50.jpg", cv2.drawKeypoints(img, sorted_sift, None, (255, 0, 255)))
cv2.imwrite("orb_top50.jpg", cv2.drawKeypoints(img, sorted_orb, None, (255, 0, 255)))

# --- Step 10: Print and explain descriptors ---
# Print the first few descriptor values for each method.
# Example: print(descriptors_sift[:2]) and print(descriptors_orb[:2])
# In your report, explain what these descriptor values represent and how they differ.
print(descriptors_sift[:2])
print(descriptors_orb[:2])

# --- Step 11: Visualize one descriptor vector ---
# TODO: Use matplotlib to create a bar chart of one descriptor vector.
# Hint: Search “matplotlib bar chart site:matplotlib.org”
# Also check how to install matplotlib if you don’t have it installed.
# (Hint: pip install matplotlib)
# Save the figure as 'sift_descriptor_plot.jpg'.
plt.figure(figsize=(10, 5))
plt.bar(list(range(1, len(descriptors_sift[0]) + 1)), descriptors_sift[0])
plt.title('SIFT Descriptor Vector')
plt.xlabel('Index')
plt.ylabel('Value')
plt.savefig('sift_descriptor_plot.jpg')
plt.close()