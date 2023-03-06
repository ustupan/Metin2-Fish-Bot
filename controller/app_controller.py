import logging
import tkinter
from typing import Dict

from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.modules.fishbot.bot import Bot
from controller.managers.settings_manager import SettingsManager
from controller.managers.threading_manager import ThreadingManager, CallableGroup
from controller.internal.view_validators.settings_validator import SettingsValidator
from view.app import App


def string_to_int_list(string):
    return [int(x, 16) for x in string[1:-1].split(",")]


def string_to_string_list(string):
    return [x for x in string[1:-1].split(",")]


def string_list_to_string(offsets):
    return '[{}]'.format(','.join(str(i) for i in [x for x in offsets]))


def offsets_to_hex_string(offsets):
    return '[{}]'.format(','.join(str(i) for i in [hex(x) for x in offsets]))


def displayed_process_name_to_id(process_name: str):
    _, process_id_str = process_name.strip().split('|')
    process_id = int(process_id_str.strip())
    return process_id


class AppController:
    def __init__(self):
        self.view_logger = ViewLogger(self.update_logs_box)
        self.settingsManager = SettingsManager()
        self.process = Process(None, None, None, None, None)
        self.view = App(
            self.view_logger,
            Process.get_process_list(),
            self.settingsManager.settings,
            self.pause_or_resume,
            self.cancel_animation,
            self.exit,
            self.load_settings,
            self.load_settings_from_file)
        self.bot = Bot(self.process, self.settingsManager.settings, self.view_logger)
        self.threadingManager = ThreadingManager(self.restart)

    def load_settings_from_file(self, path):
        self.settingsManager.load(path)  # run it on button click
        self.view.bait_keys_entry.insert(0, string_list_to_string(self.settingsManager.settings.keys_with_fish_bait))
        self.view.fishing_base_entry.insert(0, hex(self.settingsManager.settings.fishing_base_address))
        self.view.fish_caught_base_entry.insert(0, hex(self.settingsManager.settings.fish_is_caught_base_address))
        self.view.fishing_pole_thrown_offsets_entry.insert(0, offsets_to_hex_string(
            self.settingsManager.settings.pole_is_thrown_offsets))
        self.view.fishing_caught_offsets_entry.insert(0, offsets_to_hex_string(
            self.settingsManager.settings.fish_is_caught_offsets))
        self.view.message_base_entry.insert(0, hex(self.settingsManager.settings.message_base_address))
        self.view.message_offsets_entry.insert(0, offsets_to_hex_string(
            self.settingsManager.settings.message_offsets))
        self.view.sitting_on_horse_base_entry.insert(0,
                                                     hex(self.settingsManager.settings.sitting_on_horse_base_address))
        self.view.sitting_on_horse_offset_entry.insert(0, offsets_to_hex_string(
            self.settingsManager.settings.sitting_on_horse_offsets))

    def load_settings(self):
        if SettingsValidator.validateViewSettings(self.view):
            self.process = self.process.copy(
                Process.get_by_id(displayed_process_name_to_id(self.view.scaling_option_menu.get())))
            self.settingsManager.settings.fishing_base_address = int(self.view.fishing_base_entry.get(), 16)
            self.settingsManager.settings.fish_is_caught_base_address = int(self.view.fish_caught_base_entry.get(), 16)
            self.settingsManager.settings.pole_is_thrown_offsets = \
                string_to_int_list(self.view.fishing_pole_thrown_offsets_entry.get())
            self.settingsManager.settings.fish_is_caught_offsets = \
                string_to_int_list(self.view.fishing_caught_offsets_entry.get())
            self.settingsManager.settings.message_base_address = int(self.view.message_base_entry.get(), 16)
            self.settingsManager.settings.message_offsets = string_to_int_list(self.view.message_offsets_entry.get())
            self.settingsManager.settings.sitting_on_horse_base_address = \
                int(self.view.sitting_on_horse_base_entry.get(), 16)
            self.settingsManager.settings.sitting_on_horse_offsets = string_to_int_list(
                self.view.sitting_on_horse_offset_entry.get())
            self.settingsManager.settings.keys_with_fish_bait = string_to_string_list(self.view.bait_keys_entry.get())
            self.view.switch.configure(state=tkinter.NORMAL)
        else:
            self.view.switch.configure(state=tkinter.DISABLED)

    def update_logs_box(self, value_to_set):
        self.view.logs_box.configure(state='normal')
        self.view.logs_box.insert("0.0", value_to_set)
        self.view.logs_box.configure(state='disabled')
        return

    def pause_or_resume(self):

        if self.threadingManager.system_pause.is_set() is True:
            logging.info("Pausing...")
            self.threadingManager.system_pause.clear()
        else:
            logging.info("Resuming...")
            self.threadingManager.system_pause.set()

    def cancel_animation(self):
        if self.bot.cancel_animations is True:
            self.bot.cancel_animations = False
        else:
            self.bot.cancel_animations = True

    def exit(self):
        logging.info("Exiting...")
        self.threadingManager._exit = True

        # unlock the pause event so that the main loop can exit
        self.threadingManager.system_pause.set()

    def restart(self):
        self.bot.throw_attempts = 0
        self.bot.announced_pole_status = False
        self.bot.cancel_animations = False
        self.bot.last_time_pole_thrown = None
        self.view_logger.update_logs("Exception Occurred! Restarting...")

    def start(self):
        callable_groups: Dict[str, CallableGroup] = {
            "fish_and_message": CallableGroup(tasks=[self.bot.bot_loop, self.bot.message_scanner.message_scan_loop])}
        self.threadingManager.callable_groups = callable_groups
        self.threadingManager.main_func = self.view.mainloop
        self.threadingManager.start()
