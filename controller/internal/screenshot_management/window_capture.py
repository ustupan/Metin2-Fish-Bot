import os

import cv2
import numpy as np
import win32gui, win32ui, win32con


def get_png_paths(directory):
    png_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.png'):
                png_paths.append(os.path.join(root, file))
    return png_paths


class WindowCapture:

    # # properties
    # w = 0
    # h = 0
    # hwnd = None
    # cropped_x = 0
    # cropped_y = 0
    # offset_x = 0
    # offset_y = 0

    # constructor
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.w = None
        self.h = None
        self.cropped_x = None
        self.cropped_y = None
        self.offset_x = None
        self.offset_y = None

    def calculate_window_constants(self, crop_x=(0, False), crop_y=0):
        self.w = None
        self.h = None
        self.cropped_x = None
        self.cropped_y = None
        self.offset_x = None
        self.offset_y = None
        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        if crop_x[1]:
            self.w = self.w - (crop_x[0] * 2)
        else:
            self.w = self.w - crop_x[0]
        self.h = self.h - (crop_y * 2)
        self.cropped_x = crop_x[0]
        self.cropped_y = crop_y

    def get_screen_position(self, pos):
        return pos[0] + self.cropped_x, pos[1] + self.cropped_y

    def get_screenshot(self, crop_x=(0, False), crop_y=0):
        self.calculate_window_constants(crop_x, crop_y)
        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type()
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[..., :3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)
        return img
