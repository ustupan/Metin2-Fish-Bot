import ctypes
import functools
import logging
import os
import time
from typing import List

import psutil
import win32api
import win32con
import win32gui
import win32process
import win32event
import random

import pyautogui as pyautogui
import pywinauto
import pywinauto.win32functions
import pywinauto.win32structures
import pywinauto.win32defines

from controller.managers.operations_manager import OperationsManager
from pywinauto import mouse


def _prepare_lparam(message, vk):
    l_param = win32api.MapVirtualKey(vk, 0) << 16

    if message is win32con.WM_KEYDOWN:
        l_param |= 0x00000000
    else:
        l_param |= 0x50000001

    return l_param


class Process:
    def __init__(self, process_id: int, process_name: str, window_name: str, base_address, hwnd: int):
        self.process_id = process_id
        self.process_name = process_name

        self.base_address = base_address
        self.window_name = window_name
        self.hwnd = hwnd
        self.__last_window_handle = None
        self.__last_window_thread_id = None

    def copy(self, process):
        self.process_id = process.process_id
        self.process_name = process.process_name
        self.base_address = process.base_address
        self.window_name = process.window_name
        self.hwnd = process.hwnd
        self.__last_window_handle = process.__last_window_handle
        self.__last_window_thread_id = process.__last_window_thread_id
        return self

    @functools.cached_property
    def process_handle(self):
        """We don't use the handle we got while getting the process by name,
        because that handle contains sub modules,
        which we don't want while reading the memory."""
        return ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_VM_READ, False, self.process_id)

    @functools.cached_property
    def window_handle(self):
        """To focus, and send inputs"""
        if self.hwnd is not None:
            return self.hwnd
        return win32gui.FindWindow(None, self.window_name)

    @functools.cached_property
    def thread_id(self):
        """To focus, and send inputs"""
        return win32process.GetWindowThreadProcessId(self.window_handle)[0]

    def read_memory(self, address, offsets: List = None, byte=False):
        """Reads memory using a base_address and a list of offsets (optional).
        Returns a pointer and a value."""

        if byte is True:
            data = ctypes.c_ubyte(0)
            bytes_read = ctypes.c_ubyte(0)
        else:
            data = ctypes.c_uint(0)  # our data or the address pointer
            bytes_read = ctypes.c_uint(0)  # bytes read

        current_address = address

        if offsets:
            for offset in offsets:
                # Convert to int if its str
                if isinstance(offset, str):
                    offset = int(offset, 16)

                # https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory
                ctypes.windll.kernel32.ReadProcessMemory(self.process_handle, current_address, ctypes.byref(data),
                                                         ctypes.sizeof(data), ctypes.byref(bytes_read))

                # Replace the address with the new data address
                current_address = data.value + offset
        else:
            # Just read the single memory address
            ctypes.windll.kernel32.ReadProcessMemory(self.process_handle, current_address, ctypes.byref(data),
                                                     ctypes.sizeof(data),
                                                     ctypes.byref(bytes_read))

        # Return a pointer to the value and the value
        # If current offset is `None`, return the value of the last offset
        logging.debug(f"(Address: {hex(current_address)}) Value: {data.value}")
        return current_address, data.value

    def focus(self):

        """Focuses on the process window."""
        self.__last_window_handle = win32gui.GetForegroundWindow()
        # https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentthreadid
        self.__last_window_thread_id = win32api.GetCurrentThreadId()

        if self.__last_window_handle != self.window_handle:
            exc = None

            # try 2 times
            for _ in range(2):
                try:
                    # SetForegroundWindow doesn't work without sending an alt key first
                    OperationsManager.press_and_release('alt', sleep_between=0, precise=True)

                    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-attachthreadinput
                    win32process.AttachThreadInput(self.__last_window_thread_id, self.thread_id, True)
                    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setfocus
                    win32gui.SetForegroundWindow(self.window_handle)

                except Exception as e:
                    # del the attribute to update it
                    delattr(self, 'window_handle')
                    exc = e
                    time.sleep(0.1)
                else:
                    return

            raise exc

    def focus_back_to_last_window(self):
        """Focuses back to the last window that was active before focusing on our process."""
        if self.__last_window_handle != self.window_handle:
            # SetForegroundWindow doesn't work without sending 'alt' first
            OperationsManager.press_and_release('alt', sleep_between=0)

            win32process.AttachThreadInput(self.__last_window_thread_id, self.thread_id, False)
            try:
                win32gui.SetForegroundWindow(self.__last_window_handle)
            except:
                # if we couldn't focus back, just ignore
                pass

    @staticmethod
    def kill_by_name(names: List[str]):
        """Kill every process by specified list of names."""
        names = list(map(lambda x: x.casefold(), names))

        for proc in psutil.process_iter():
            if proc.name().casefold() in names:
                try:
                    proc.kill()
                except psutil.AccessDenied:
                    logging.debug(f'Could not kill process "{proc.name()}". Ignoring.')
                except psutil.NoSuchProcess:
                    pass

    @staticmethod
    def char2key(c):
        """Converts a key to a Windows Virtual Key code."""

        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscanw
        result = win32api.VkKeyScan(c)

        # shift_state = (result & 0xFF00) >> 8
        vk_key = result & 0xFF  # remove the shift state

        return vk_key

    def send_mouse_click(self, focus: bool = True, x=None, y=None, hwnd=None, start_from_center=False, button='left',
                         instant=False):
        mutex_name = "SendOperationMutex"
        mutex = win32event.CreateMutex(None, False, mutex_name)
        try:
            win32event.WaitForSingleObject(mutex, win32event.INFINITE)
            if focus is True:  # focus if needed
                self.focus()
            app = pywinauto.Application().connect(handle=hwnd)
            window = app.window(handle=hwnd)
            rect = window.rectangle()
            # Get the top-left coordinates of the window on the screen
            left, top = rect.left, rect.top
            if not start_from_center:
                # Assign some random values in case of logs
                x = x + random.randint(10, 15)
                y = y + random.randint(10, 15)
                random_float = random.uniform(0.1, 0.15)
                pyautogui.moveTo(x + left, y + top, duration=random_float)
                random_float = random.uniform(0.13, 0.15)
                pyautogui.click(button=button, duration=random_float)
            else:
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                random_float = random.uniform(0.01, 0.05)
                if instant:
                    random_float = 0.0
                pyautogui.moveTo(center_x - x, center_y + y, duration=random_float)
                random_float = random.uniform(0.1, 0.13)
                if instant:
                    random_float = 0.0
                pyautogui.click(button=button, duration=random_float)
        finally:
            win32event.ReleaseMutex(mutex)

    def send_input(self, *keys: str,
                   sleep_between_keys: float = 0,
                   sleep_between_presses: float = 0,
                   focus: bool = True,
                   focus_back: bool = False,
                   send_to_process: bool = False):
        mutex_name = "SendOperationMutex"
        mutex = win32event.CreateMutex(None, False, mutex_name)
        try:
            win32event.WaitForSingleObject(mutex, win32event.INFINITE)
            """Sends a key input straight to the process. This took me a lot of time, but it was worth it."""
            if focus is True:  # focus if needed
                self.focus()
                time.sleep(sleep_between_presses)

            for key in keys:
                if send_to_process is False:
                    OperationsManager.press_and_release(key, sleep_between=sleep_between_presses, precise=True)
                else:
                    # split combination
                    _keys = key.split('+')

                    # get the virtual key code
                    vk = self.char2key(_keys[0])
                    if 'ctrl' in _keys:
                        vk = 0x200 | vk
                    win32api.SendMessage(self.window_handle, win32con.WM_KEYDOWN, vk,
                                         _prepare_lparam(win32con.WM_KEYDOWN, vk))
                    time.sleep(sleep_between_presses)
                    win32api.PostMessage(self.window_handle, win32con.WM_KEYUP, vk,
                                         _prepare_lparam(win32con.WM_KEYUP, vk))

                time.sleep(sleep_between_keys)
            if focus_back is True:
                self.focus_back_to_last_window()
        finally:
            win32event.ReleaseMutex(mutex)
            time.sleep(0.2)

    @classmethod
    def get_by_name(cls, process_name: str, window_name: str) -> "Process":
        """Finds a process by name and returns a Process object."""

        for process_id in win32process.EnumProcesses():
            # If process_id is the same as this program, skip it
            if process_id == -1:
                continue

            handle = None
            # Try to read the process memory
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                                              True, process_id)
            except:
                continue
            else:
                # iterate over an array of base addresses of each module
                for base_address in win32process.EnumProcessModules(handle):
                    # Get the name of the module
                    current_name = str(win32process.GetModuleFileNameEx(handle, base_address))

                    # compare it
                    if process_name.casefold() in current_name.casefold():
                        logging.debug(f"Base address of {process_name} ({process_id}): {hex(base_address)}")
                        return cls(process_id, process_name, window_name, base_address)

            finally:
                if handle:
                    # close the handle as we don't need it anymore
                    win32api.CloseHandle(handle)

        raise Exception(f"{process_name} could not be found.")

    @staticmethod
    def get_window_by_pid(pid):
        """
        Get the window handle for the first top-level window associated with
        the given process ID (pid).
        """
        hwnds = []

        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                try:
                    window_pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                except:
                    # Ignore windows that don't have a process ID (e.g. the desktop window)
                    return
                if window_pid == pid:
                    hwnds.append(hwnd)

        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    @classmethod
    def get_by_id(cls, process_id: int) -> "Process":
        """Finds a process by id and returns a Process object."""
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                                          True, process_id)
            hwnd = cls.get_window_by_pid(process_id)
            for base_address in win32process.EnumProcessModules(handle):
                # Get the name of the module
                current_name = str(win32process.GetModuleFileNameEx(handle, base_address))
                return cls(process_id, current_name, "", base_address, hwnd)
        except:
            Exception(f" Process with id: {process_id} could not be found.")

    @staticmethod
    def get_process_list():
        process_list = []
        process_ids = win32process.EnumProcesses()

        for process_id in process_ids:
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                                              True, process_id)
                hwnd = Process.get_window_by_pid(process_id)
                if hwnd is None:
                    continue
                exe_name = win32process.GetModuleFileNameEx(handle, 0)
                if "Windows" in exe_name:
                    continue
                if "metin" not in exe_name:
                    continue
                exe_name = os.path.basename(win32process.GetModuleFileNameEx(handle, 0))
                process_list.append(f"{exe_name} | {process_id}")
            except:
                Exception(f" Process with id: {process_id} could not be found.")
        return process_list

    # image stuff
    def get_window_size(self) -> (int, int):
        rect = win32gui.GetClientRect(self.window_handle)
        return rect[2], rect[3]

    def client_to_window_coords(self, client_coord_x: int, client_coord_y: int) -> (int, int):
        return win32gui.ClientToScreen(self.window_handle, (int(client_coord_x), int(client_coord_y)))

    def __del__(self):
        """Close the handle when our object gets garbage collected."""
        if self.process_handle:
            ctypes.windll.kernel32.CloseHandle(self.process_handle)
