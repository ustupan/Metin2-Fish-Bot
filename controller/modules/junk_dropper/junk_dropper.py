from typing import List
from uuid import UUID

import win32event
from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.managers.settings_manager import Settings
from controller.modules.junk_dropper.vision import Vision
from controller.modules.junk_dropper.window_capture import WindowCapture

import datetime
import time

CONFIRM_DROP_CORDS = (50, 30)


class JunkDropper:

    def __init__(self, app_id: UUID, inventory_paths: List, image_paths_to_be_dropper: List, delay_seconds: int, process: Process, settings: Settings, logger: ViewLogger):
        self.app_id = app_id
        self.seconds_to_add_to_next_planned_dropping = delay_seconds
        self.logger = logger
        self.process = process
        self.settings = settings
        self.win_cap = None
        self.delay_seconds = delay_seconds
        self.next_planned_dropping = None
        self.image_paths_to_be_dropper = image_paths_to_be_dropper
        self.inventory_paths = inventory_paths

    def start_dropping(self):
        time.sleep(10)
        if self.next_planned_dropping is None:
            self.next_planned_dropping = datetime.datetime.now()
        time_diff_sec = (self.next_planned_dropping - datetime.datetime.now()).total_seconds()
        if time_diff_sec <= 10:
            mutex_name = self.app_id.hex
            mutex = win32event.CreateMutex(None, False, mutex_name)
            try:
                win32event.WaitForSingleObject(mutex, win32event.INFINITE)
                for inventory in self.inventory_paths:
                    points = []
                    self.click_on_inventory(inventory)
                    self.win_cap = WindowCapture(self.process.hwnd)
                    screenshot = self.win_cap.get_screenshot()
                    for path_to_be_dropped in self.image_paths_to_be_dropper:
                        points = points + Vision(path_to_be_dropped).find(screenshot, 0.8)
                    for point in points:
                        self.single_drop_operation(point)
                    self.next_planned_dropping = self.next_planned_dropping + datetime.timedelta(seconds=self.delay_seconds)
                self.click_on_inventory(self.inventory_paths[0])
            finally:
                win32event.ReleaseMutex(mutex)

    def click_on_inventory(self, inventory_path):
        self.win_cap = WindowCapture(self.process.hwnd)
        screenshot = self.win_cap.get_screenshot()
        points = Vision(inventory_path).find(screenshot, 0.8)
        if points:
            self.process.send_mouse_click(True, points[0][0], points[0][1], hwnd=self.process.hwnd)

    def single_drop_operation(self, point):
        self.process.send_mouse_click(True, point[0], point[1], hwnd=self.process.hwnd)
        self.process.send_mouse_click(True, point[0] - 170, point[1], hwnd=self.process.hwnd)
        self.process.send_mouse_click(True, CONFIRM_DROP_CORDS[0], CONFIRM_DROP_CORDS[1], hwnd=self.process.hwnd,
                                      start_from_center=True)
        self.logger.update_logs("Dropped an junk item...")
