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
    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, screenshot, threshold=0.8):
        img_rgb = screenshot
        template = self.needle_img
        points = []
        w, h = template.shape[:-1]

        res = cv.matchTemplate(img_rgb, template, cv.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):  # Switch columns and rows
            points.append(pt)
            cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        return filter_points(points)
