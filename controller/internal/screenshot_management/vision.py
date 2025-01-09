import cv2 as cv
import numpy as np


def filter_points(points):
    new_points = []
    curr_point = None
    for point in points:
        should_not_be_added = False
        if not new_points:
            new_points.append(point)
        else:
            for new_point in new_points:
                curr_point = point
                if abs(new_point[0] - point[0]) + abs(new_point[1] - point[1]) < 8:
                    should_not_be_added = True
            if not should_not_be_added:
                new_points.append(curr_point)
    return new_points


class Vision:

    # constructor
    def __init__(self, transform_into_screen_pos: callable, method=cv.TM_CCOEFF_NORMED):
        self.transform_into_screen_pos = transform_into_screen_pos
        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, screenshot, needle_img_path, threshold=0.8):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Save the dimensions of the needle image
        # needle_w = needle_img.shape[1]
        # needle_h = needle_img.shape[0]
        img_rgb = screenshot
        template = needle_img
        points = []
        w, h = template.shape[:-1]

        res = cv.matchTemplate(img_rgb, template, cv.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):  # Switch columns and rows
            points.append(self.transform_into_screen_pos(pt))
            cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        return filter_points(points)


    def find2(self, screenshot, needle_img_path, threshold=0.8):
        # Load the image we're trying to match
        needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Convert the needle image to a single-channel (grayscale) image
        needle_gray = cv.cvtColor(needle_img, cv.COLOR_BGR2GRAY)

        # Save the dimensions of the needle image
        needle_w = needle_img.shape[1]
        needle_h = needle_img.shape[0]

        img_rgb = screenshot

        # Convert the input image to a single-channel (grayscale) image
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)

        points = []

        # Ensure the depth and type match
        needle_gray = needle_gray.astype(np.float32)  # Convert template to float32 if needed
        img_gray = img_gray.astype(np.float32)  # Convert input image to float32 if needed

        # Check the number of dimensions and assert if necessary
        assert needle_gray.ndim <= 2 and img_gray.ndim <= 2, "Images must have at most 2 dimensions."

        # Perform the template matching
        res = cv.matchTemplate(img_gray, needle_gray, cv.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):  # Switch columns and rows
            points.append(self.transform_into_screen_pos(pt))
            cv.rectangle(img_rgb, pt, (pt[0] + needle_w, pt[1] + needle_h), (0, 0, 255), 2)

        return filter_points(points)
