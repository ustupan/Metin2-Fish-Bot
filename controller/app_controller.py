import logging
from threading import Event, Thread
from typing import List

from controller.internals.bot import Bot
from controller.managers.settings_loader import SettingsLoader
from view.app import App


class AppController:
    def __init__(self):
        self.settingsLoader = SettingsLoader()
        self.view = App(self.settingsLoader.settings)
        self.settingsLoader.load()  # run it on button click
        self.bot = Bot(self.settingsLoader.settings)

        self.sub_tasks = [self.bot.bot_loop, self.bot.message_scanner_loop]
        self.threads: List[Thread] = list()
        self.thread_exception: Exception = None

        self.pause = Event()
        self._exit = False

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
        # init threads
        if self.sub_tasks:
            for sub_task in self.sub_tasks:
                self.threads.append(Thread(target=self.runner_loop, args=(sub_task,)))

        # start threads
        for thread in self.threads:
            thread.start()

        # start view on the main thread
        self.view.mainloop()

        # wait for them to complete
        for thread in self.threads:
            thread.join()

        # raise if there was an exception
        if self.thread_exception:
            raise self.thread_exception
