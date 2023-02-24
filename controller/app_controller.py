import logging
from typing import Dict

from controller.internals.bot import Bot
from controller.managers.settings_loader import SettingsLoader
from controller.managers.threading_manager import ThreadingManager, CallableGroup
from view.app import App


def string_to_int_list(string):
    return [int(x, 16) for x in string[1:-1].split(",")]


def offsets_to_hex_string(offsets):
    return '[{}]'.format(','.join(str(i) for i in [hex(x) for x in offsets]))


class AppController:
    def __init__(self):
        self.settingsLoader = SettingsLoader()
        self.view = App(self.settingsLoader.settings,
                        self.pause_or_resume,
                        self.exit,
                        self.load_settings,
                        self.load_settings_from_file)
        self.bot = Bot(self.settingsLoader.settings)
        self.threadingManager = ThreadingManager()

    def load_settings_from_file(self, path):
        self.settingsLoader.load(path)  # run it on button click
        self.view.fishing_base_entry.insert(0, hex(self.settingsLoader.settings.fishing_base_address))
        self.view.fish_caught_base_entry.insert(0, hex(self.settingsLoader.settings.fish_is_caught_base_address))
        self.view.fishing_pole_thrown_offsets_entry.insert(0, offsets_to_hex_string(
            self.settingsLoader.settings.pole_is_thrown_offsets))
        self.view.fishing_caught_offsets_entry.insert(0, offsets_to_hex_string(
            self.settingsLoader.settings.fish_is_caught_offsets))
        self.view.message_base_entry.insert(0, hex(self.settingsLoader.settings.message_base_address))
        self.view.message_offsets_entry.insert(0, offsets_to_hex_string(
            self.settingsLoader.settings.message_offsets))

    def load_settings(self):
        self.settingsLoader.settings.fishing_base_address = int(self.view.fishing_base_entry.get(), 16)
        self.settingsLoader.settings.fish_is_caught_base_address = int(self.view.fish_caught_base_entry.get(), 16)
        self.settingsLoader.settings.pole_is_thrown_offsets = \
            string_to_int_list(self.view.fishing_pole_thrown_offsets_entry.get())
        self.settingsLoader.settings.fish_is_caught_offsets = \
            string_to_int_list(self.view.fishing_caught_offsets_entry.get())
        self.settingsLoader.settings.message_base_address = int(self.view.message_base_entry.get(), 16)
        self.settingsLoader.settings.message_offsets = string_to_int_list(self.view.message_offsets_entry.get())

    def pause_or_resume(self):

        if self.threadingManager.system_pause.is_set() is True:
            logging.info("Pausing...")
            self.threadingManager.system_pause.clear()
        else:
            logging.info("Resuming...")
            self.threadingManager.system_pause.set()

    def exit(self):
        logging.info("Exiting...")
        self.threadingManager._exit = True

        # unlock the pause event so that the main loop can exit
        self.threadingManager.system_pause.set()

    def start(self):
        callable_groups: Dict[str, CallableGroup] = {
            "fish_message": CallableGroup(tasks=[self.bot.bot_loop, self.bot.message_scanner.message_scan_loop])}
        self.threadingManager.callable_groups = callable_groups
        self.threadingManager.main_func = self.view.mainloop
        self.threadingManager.start()

