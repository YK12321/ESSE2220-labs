"""
Lab 8: Feature Matching (BFMatcher + FLANN + Filtering)
-------------------------------------------------------
Instructions:
1. Choose ONE detector at a time (SIFT or ORB).
2. Extract features and measure extraction time.
3. Run BFMatcher (normal and crossCheck).
4. Run FLANN with
5. Apply THREE filters:
       - Distance Threshold
       - Lowe's Ratio Test
       - Symmetry Check (BFMatcher crossCheck=True)
6. Visualize all results
7. Save all required images.
8. Repeat with the second detector.
"""

import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Step 1: Load images
# ---------------------------------------------------------
img1 = cv2.imread("socal-fire_00000325_pre_disaster.png", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("socal-fire_00000325_post_disaster.png", cv2.IMREAD_GRAYSCALE)


# ---------------------------------------------------------
# Step 2: Choose ONE detector (uncomment one)
# ---------------------------------------------------------

# ---- SIFT ----
detector = cv2.SIFT_create()

# ---- ORB ----
# detector = cv2._________(_________)


# ---------------------------------------------------------
# Step 3: Detect + compute (with timing)
# ---------------------------------------------------------
t0 = time.time()
kp1, des1 = detector.detectAndCompute(img1, None)
t1 = time.time()
kp2, des2 = detector.detectAndCompute(img2, None)
t2 = time.time()

print("Keypoints img1:", len(kp1))
print("Keypoints img2:", len(kp2))

print("Descriptor shapes:", des1.shape, des2.shape)

print("Extraction time (img1):", t1 - t0)
print("Extraction time (img2):", t2 - t1)


# ---------------------------------------------------------
# Step 4: Create matchers (BF + crossCheck + FLANN)
# ---------------------------------------------------------

# BF normal matcher
# (For SIFT → NORM_L2, For ORB → NORM_HAMMING)
bf = cv2.BFMatcher(cv2.NORM_L2)

# BF symmetry check matcher
bf_cross = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

# FLANN matcher
# algorithm = type of search structure (1 = KDTree, 6 = LSH)
# trees = number of trees (more trees → slower but more accurate)
# checks = how many leaf nodes to search (higher = better accuracy)
flann = cv2.FlannBasedMatcher(
    indexParams = dict(algorithm=1, trees=5),
    searchParams = dict(checks=50)
)


# ---------------------------------------------------------
# Step 5: Perform matching (raw outputs)
# ---------------------------------------------------------

# Best match for each descriptor
matches_bf = bf.match(des1, des2)

# Two best matches (m,n) for each descriptor
knn_bf = bf.knnMatch(des1, des2, k=2)

# FLANN single best match (approximate)
matches_flann = flann.match(des1, des2)

# FLANN two best matches (approximate)
knn_flann = flann.knnMatch(des1, des2, k=2)


# ---------------------------------------------------------
# Step 6: Filtering methods
# ---------------------------------------------------------

# Distance Threshold
# Typical range:
#   SIFT: 150–300
#   ORB:  20–60
def distance_filter(matches, threshold):
    return [m for m in matches if m.distance < threshold]


# Lowe’s Ratio Test (m.distance < ratio * n.distance)
# Typical range: 0.6–0.8
def ratio_test(knn_matches, ratio=0.75):
    good = []
    for m, n in knn_matches:
        if m.distance < ratio * n.distance:
            good.append(m)
    return good


# Symmetry Check: already done using BFMatcher crossCheck=True
matches_sym = bf_cross.match(des1, des2)


# ---------------------------------------------------------
# Step 7: Apply ONE method at a time
# ---------------------------------------------------------
# Students should comment/uncomment ONE line:

# chosen_matches = matches_bf                    # Raw BF
# chosen_matches = matches_flann                # Raw FLANN
# chosen_matches = distance_filter(matches_bf, threshold=__________)
# chosen_matches = ratio_test(knn_bf, ratio=__________)
# chosen_matches = matches_sym                  # Symmetry check
# chosen_matches = distance_filter(matches_flann, threshold=__________)
# chosen_matches = ratio_test(knn_flann, ratio=__________)


# ---------------------------------------------------------
# Step 8: Visualization (ONE LINE ONLY)
# ---------------------------------------------------------

img_out = cv2.drawMatches(img1, kp1, img2, kp2, chosen_matches, None)
cv2.imwrite("raw_flann.jpg", img_out)


# ---------------------------------------------------------
# REQUIRED OUTPUT IMAGES
# ---------------------------------------------------------
"""
For EACH detector (SIFT, ORB):

1. raw_bf.jpg               (matches_bf)
2. raw_flann.jpg            (matches_flann)
3. bf_distance.jpg          (distance filter on BF)
4. bf_ratio.jpg             (ratio test on BF)
5. bf_symmetry.jpg          (crossCheck output)
6. flann_distance.jpg       (distance filter on FLANN)
7. flann_ratio.jpg          (ratio test on FLANN)

Total: 7 images per detector → 14 images in the lab.
"""