import cv2
import numpy as np


def loadImage(path):
    loadedImage = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return loadedImage

def prePipeline(images, type):
    if str(type).casefold() == "orb":
        detector = cv2.ORB_create()
        matcherType = cv2.NORM_HAMMING
    else:
        detector = cv2.SIFT_create()
        matcherType = cv2.NORM_L2

    kps, descs = [], []
    for i in images:
        kpi, desci = detector.detectAndCompute(i, None)
        kps.append(kpi)
        descs.append(desci)
    
    bf = cv2.BFMatcher(matcherType)
    matches_bf = bf.match(descs[0], descs[1])

    return matches_bf, kps, descs

def pipelineA1(images, kps, matches, distance_thresh= 50):
    filteredMatches = [m for m in matches if m.distance < distance_thresh]
    
    match_img = cv2.drawMatches(images[0], kps[0], images[1], kps[1], filteredMatches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    return match_img

def pipelineA2(images, kps, matches):
    if len(matches) < 4:
        print("Not enough matches to compute homography.")
        return None, None, None

    src_pts = np.float32([kps[0][m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kps[1][m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Compute Homography using RANSAC
    H_A, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 10.0)
    matchesMask = mask.ravel().tolist()

    # Draw inliers
    draw_params_inliers = dict(matchColor=(0, 255, 0), # Green for inliers
                               singlePointColor=None,
                               matchesMask=matchesMask,
                               flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    img_inliers = cv2.drawMatches(images[0], kps[0], images[1], kps[1], matches, None, **draw_params_inliers) # Here, the **draw_params_inliers unpacks the dictionary into keyword arguments

    # Draw outliers
    outliersMask = [1 - m for m in matchesMask]
    draw_params_outliers = dict(matchColor=(0, 0, 255), # Red for outliers
                                singlePointColor=None,
                                matchesMask=outliersMask,
                                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    img_outliers = cv2.drawMatches(images[0], kps[0], images[1], kps[1], matches, None, **draw_params_outliers)

    return H_A, img_inliers, img_outliers

def pipelineB(images, type):
    """
    Pipeline B: With Location Filter
    Similar to A but adds a location filter for keypoints to isolate the cathedral.
    """
    # 1. Detect Keypoints and Descriptors (ORB or SIFT)
    #    You can use the code from prePipeline() here or call it, 
    #    but you need access to the raw keypoints and descriptors BEFORE matching.
    if str(type).casefold() == "orb":
        detector = cv2.ORB_create()
        matcherType = cv2.NORM_HAMMING
    else:
        detector = cv2.SIFT_create()
        matcherType = cv2.NORM_L2

    kps, descs = [], []
    for i in images:
        kpi, desci = detector.detectAndCompute(i, None)
        kps.append(kpi)
        descs.append(desci)


    # 2. Define Cutoff Values
    #    Determine the x-coordinates to crop the left and right sides.
    #    img1_x_min, img1_x_max = ... (e.g., 100, width - 100)
    #    img2_x_min, img2_x_max = ...
    boundaries = images[0].shape[1]
    # Image 1
    img1_x_min = 65
    img1_x_max = boundaries - 50
    img1_y_min = 5
    img1_y_max = images[0].shape[0] - 10
    # Image 2
    img2_x_min = 50
    img2_x_max = boundaries - 55
    img2_y_min = 0
    img2_y_max = images[1].shape[0] - 20

    
    # 3. Filter Keypoints and Descriptors
    #    Iterate through the keypoints for Image 1:
    #      - Check if kp.pt[0] (x-coordinate) is within [img1_x_min, img1_x_max].
    #      - If yes, keep the keypoint and its corresponding descriptor.
    #    Repeat for Image 2 using its specific cutoff values.
    #    IMPORTANT: Ensure keypoints and descriptors remain synchronized (same indices).
    for i in kps:
        for j in kps[i]:



    
    # 4. Match Descriptors
    #    Use BFMatcher (as in prePipeline) to match the *filtered* descriptors.
    
    # 5. Compute Homography (RANSAC)
    #    Use the filtered matches to compute the homography matrix, 
    #    similar to pipelineA2().
    pass

def main():
    image_paths = ["img1.jpg", "img2.jpg"]
    images = [loadImage(path) for path in image_paths]
    matches = prePipeline(images, "FLANN")
    
    # Pipeline A1
    result_image = pipelineA1(images, matches[1], matches[2], matches[0])
    cv2.imwrite("A1DistanceFiltered.jpg", result_image)

    # Pipeline A2
    H_A, inliers_img, outliers_img = pipelineA2(images, matches[1], matches[0])
    
    if H_A is not None:
        print("Pipeline A2\n")
        print("Homography Matrix H_A:\n", H_A)
        cv2.imwrite("A2Inliers.jpg", inliers_img)
        cv2.imwrite("A2Outliers.jpg", outliers_img)

    # Pipeline B
    HA, inliersImgB, outliersImgB = pipelineB
    if HA is not None:
        print("Pipeline B\n")
        print("Homography Matrix H_A:\n", HA)
        cv2.imwrite("A2Inliers.jpg", inliers_img)
        cv2.imwrite("A2Outliers.jpg", outliers_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()