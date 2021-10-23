# midorina.dev
import logging
import random
import time
from threading import Event, Thread
from typing import List, Optional

import keyboard


class Manager:
    def __init__(self, main_func: callable, sub_tasks: Optional[List[callable]] = None, quit_key: str = 'ctrl+q',
                 pause_key: str = 'ctrl+p'):
        self.main_func = main_func
        self.sub_tasks = sub_tasks

        self.quit_key = quit_key
        self.pause_key = pause_key

        self.threads: List[Thread] = list()
        self.thread_exception: Exception = None

        self.pause = Event()
        self._exit = False

        # remove previous hotkeys to prevent multiple of those in case of a restart
        try:
            keyboard.unhook_all_hotkeys()
        except AttributeError:
            pass

        keyboard.add_hotkey(quit_key, lambda: self.exit())
        keyboard.add_hotkey(pause_key, lambda: self.pause_or_resume())

        # start
        self.pause.set()

    def pause_or_resume(self):
        if self.pause.is_set() is True:
            logging.info("Pausing...")
            self.pause.clear()
        else:
            logging.info("Resuming...")
            self.pause.set()

    def exit(self):
        logging.info("Exiting...")
        self._exit = True

        # unlock the pause event so that the main loop can exit
        self.pause.set()

    def runner_loop(self, func: callable):
        while True:
            # wait if we're paused
            if self.pause.is_set() is False:
                self.pause.wait()

            # exit if "self._exit" is true
            if self._exit is True:
                return

            try:
                # execute the function
                func()
            except Exception as e:
                # if it raised an error, save it and return
                self.thread_exception = e
                return

    def start(self):
        logging.info(f'Starting in 2 seconds. Press "{self.pause_key}" to pause/resume and "{self.quit_key}" to exit.')
        time.sleep(2.0)

        # init threads
        self.threads.append(Thread(target=self.runner_loop, args=(self.main_func,)))
        if self.sub_tasks:
            for sub_task in self.sub_tasks:
                self.threads.append(Thread(target=self.runner_loop, args=(sub_task,)))

        # start threads
        for thread in self.threads:
            thread.start()

        # wait for them to complete
        for thread in self.threads:
            thread.join()

        # raise if there was an exception
        if self.thread_exception:
            raise self.thread_exception

    @staticmethod
    def press_and_release(button: str,
                          sleep_before: float = 0,
                          sleep_between: float = 0,
                          sleep_after: float = 0,
                          precise: bool = False):
        if precise is True:
            sleep = time.sleep
        else:
            sleep = Manager.human_sleep

        sleep(sleep_before)
        keyboard.press(button)
        sleep(sleep_between)
        keyboard.release(button)
        sleep(sleep_after)

    @staticmethod
    def human_sleep(length: float, interval: float = None):
        # 10% inconsistency
        interval = interval or length / 10
        time.sleep(random.uniform(length - interval, length + interval))
