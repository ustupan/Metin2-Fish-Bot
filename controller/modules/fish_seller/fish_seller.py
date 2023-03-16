from typing import List
from uuid import UUID

import cv2
import win32event
from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.managers.settings_manager import Settings
from controller.internal.screenshot_management.vision import Vision
from controller.internal.screenshot_management.window_capture import WindowCapture

import datetime
import time

from controller.modules.fish_seller.fish_sell import FishSell

CONFIRM_SELL_CORDS = (30, 50)

INPUT_KWARGS = {
    'send_to_process': False,
    'focus': True,
    'sleep_between_presses': 0.03,
    'sleep_between_keys': 0.06
}


class FishSeller:

    def __init__(self, app_id: UUID, inventory_paths: List, fishes_to_be_sold: List[FishSell], delay_seconds: int,
                 free_slot_path, process: Process, settings: Settings, logger: ViewLogger):
        self.app_id = app_id
        self.seconds_to_add_to_next_planned_selling = delay_seconds
        self.logger = logger
        self.process = process
        self.settings = settings
        self.win_cap = None
        self.delay_seconds = delay_seconds
        self.next_planned_selling = datetime.datetime.now() + datetime.timedelta(seconds=15)
        self.fishes_to_be_sold = fishes_to_be_sold
        self.inventory_paths = inventory_paths
        self.free_slot_image_path = free_slot_path

    def start_selling(self):
        time.sleep(0.2)
        time_diff_sec = (self.next_planned_selling - datetime.datetime.now()).total_seconds()
        if time_diff_sec <= 10:
            self.next_planned_selling = self.next_planned_selling + \
                                        datetime.timedelta(seconds=self.delay_seconds)
            mutex_name = self.app_id.hex
            mutex = win32event.CreateMutex(None, False, mutex_name)
            try:
                win32event.WaitForSingleObject(mutex, win32event.INFINITE)
                for inventory in self.inventory_paths:
                    self.click_on_inventory(inventory)
                    self.win_cap = WindowCapture(self.process.hwnd)
                    for fish_to_be_sold in self.fishes_to_be_sold:
                        screenshot = self.win_cap.get_screenshot((1000, False), 100)
                        points = Vision(self.win_cap.get_screen_position).find(screenshot,
                                                                               fish_to_be_sold.image_path, 0.9)
                        for point in points:
                            time.sleep(0.6)
                            screenshot = self.win_cap.get_screenshot((300, True), 100)
                            free_slot_points = Vision(self.win_cap.get_screen_position).find(
                                screenshot, self.free_slot_image_path, 0.8)
                            if free_slot_points:
                                self.single_sell_operation(point, fish_to_be_sold.item_price, free_slot_points[0])
                            else:
                                self.start_selling()
                                win32event.ReleaseMutex(mutex)
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

    def single_sell_operation(self, item_point, item_price, free_slot_point):
        self.process.send_mouse_click(True, item_point[0], item_point[1], hwnd=self.process.hwnd)
        self.process.send_mouse_click(True, free_slot_point[0], free_slot_point[1], hwnd=self.process.hwnd)
        price_symbols = list(str(item_price))
        self.process.send_input('right', 'backspace', 'backspace', 'backspace', 'backspace',
                                'backspace', 'backspace', 'backspace', 'backspace', 'backspace',
                                'backspace', *price_symbols,
                                **INPUT_KWARGS)
        self.process.send_mouse_click(True, CONFIRM_SELL_CORDS[0], CONFIRM_SELL_CORDS[1], hwnd=self.process.hwnd,
                                      start_from_center=True)
        # self.logger.update_logs("Sold an item for " + item_price)
