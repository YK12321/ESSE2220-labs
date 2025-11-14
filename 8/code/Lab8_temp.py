"""Lab 8 – Section 4 helper script.

This streamlined version only gathers the numbers needed for
Section 4 of the report (feature extraction time + descriptor info
for both SIFT and ORB). No matchers or images are produced here.
"""

from pathlib import Path
import time

import cv2


IMAGE_NAMES = {
    "pre": "socal-fire_00000325_pre_disaster.png",
    "post": "socal-fire_00000325_post_disaster.png",
}


def load_images():
    """Load the grayscale satellite pair and fail loudly if missing."""
    base_dir = Path(__file__).resolve().parent
    images = {}
    for label, name in IMAGE_NAMES.items():
        path = base_dir / name
        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not open {path}")
        images[label] = img
    return images


def time_extraction(detector, image, warmup=True):
    """Detect keypoints/descriptors and report duration."""
    if warmup:
        # First call primes OpenCV's internal buffers so the timed run
        # measures steady-state performance instead of one-time setup cost.
        detector.detectAndCompute(image, None)
    start = time.perf_counter()
    keypoints, descriptors = detector.detectAndCompute(image, None)
    duration = time.perf_counter() - start
    return keypoints, descriptors, duration


def describe_descriptors(descriptors):
    if descriptors is None:
        return "None", "None"
    return str(descriptors.shape), str(descriptors.dtype)


def main():
    images = load_images()
    detector_factories = {
        "SIFT": cv2.SIFT_create,
        "ORB": cv2.ORB_create,
    }

    for detector_name, create_detector in detector_factories.items():
        print(f"=== {detector_name} ===")
        for label, image in images.items():
            detector = create_detector()
            keypoints, descriptors, duration = time_extraction(detector, image)
            shape, dtype = describe_descriptors(descriptors)
            print(
                f"{label.upper()} | keypoints: {len(keypoints):5d} | "
                f"descriptor shape: {shape} | dtype: {dtype}"
            )
            print(f"Extraction time: {duration:.4f} s")
        print()


if __name__ == "__main__":
    main()