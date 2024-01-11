from typing import List
from uuid import UUID

import win32event
from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.managers.settings_manager import Settings
from controller.internal.screenshot_management.vision import Vision
from controller.internal.screenshot_management.window_capture import WindowCapture

import datetime
import time


class Clicker:

    def __init__(self, app_id: UUID, inventory_paths: List, image_paths_to_be_clicked: List, delay_seconds: int,
                 process: Process, settings: Settings, logger: ViewLogger):
        self.app_id = app_id
        self.seconds_to_add_to_next_planned_dropping = delay_seconds
        self.logger = logger
        self.process = process
        self.settings = settings
        self.win_cap = None
        self.delay_seconds = delay_seconds
        self.next_planned_click = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.image_paths_to_be_clicked = image_paths_to_be_clicked
        self.inventory_paths = inventory_paths

    def click(self):
        time.sleep(0.2)
        time_diff_sec = (self.next_planned_click - datetime.datetime.now()).total_seconds()
        if time_diff_sec <= 10:
            self.next_planned_click = self.next_planned_click + \
                                      datetime.timedelta(seconds=self.delay_seconds)

            mutex_name = self.app_id.hex
            mutex = win32event.CreateMutex(None, False, mutex_name)
            try:
                win32event.WaitForSingleObject(mutex, win32event.INFINITE)
                for inventory in self.inventory_paths:
                    points = []
                    self.click_on_inventory(inventory)
                    self.win_cap = WindowCapture(self.process.hwnd)
                    screenshot = self.win_cap.get_screenshot((900, False), 0)
                    for path_to_be_dropped in self.image_paths_to_be_clicked:
                        points = points + Vision(self.win_cap.get_screen_position).find(screenshot,
                                                                                        path_to_be_dropped, 0.8)
                    for point in points:
                        self.single_double_click_operation(point)
                        self.click()
                        return
                self.click_on_inventory(self.inventory_paths[0])
            finally:
                win32event.ReleaseMutex(mutex)

    def click_on_inventory(self, inventory_path):
        self.win_cap = WindowCapture(self.process.hwnd)
        screenshot = self.win_cap.get_screenshot()
        points = Vision(self.win_cap.get_screen_position).find(screenshot, inventory_path, 0.8)
        if points:
            self.process.send_mouse_click(True, points[0][0], points[0][1], hwnd=self.process.hwnd)

    def single_double_click_operation(self, point):
        self.process.send_mouse_click(True, point[0], point[1], hwnd=self.process.hwnd, button='right')
        self.logger.update_logs("Double Clicked an item...")
