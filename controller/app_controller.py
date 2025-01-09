import logging
import tkinter
from typing import Dict

from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.modules.captcha_resolver.captcha_resolver import CaptchaResolver
from controller.modules.double_clicker.clicker import Clicker
from controller.modules.fish_seller.fish_seller import FishSeller
from controller.modules.fishbot.bot import Bot
from controller.managers.settings_manager import SettingsManager
from controller.managers.threading_manager import ThreadingManager, CallableGroup
from controller.modules.junk_dropper.junk_dropper import JunkDropper
from view.app import App
import uuid


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


def validate_process_name(process_name: str):
    return len(process_name.strip().split('|')) < 2


PATH_TO_SETTINGS = 'settings/memory_settings.json'


class AppController:
    def __init__(self):
        self.app_identifier = uuid.uuid4()

        self.view_logger = ViewLogger(self.update_logs_box)
        self.settingsManager = SettingsManager()
        self.process = Process(None, None, None, None, None)
        self.view = App(
            self.view_logger,
            Process.get_process_list(),
            self.settingsManager.settings,
            self.pause_or_resume,
            self.cancel_animation,
            self.drop_items,
            self.marble_click,
            self.sell_items,
            self.reply_to_messages,
            self.exit,
            self.load_settings,
            self.load_settings_from_file)
        self.view_logger.app_id = self.view.scaling_option_menu.get()
        self.bot = Bot(self.app_identifier, self.process, self.settingsManager.settings, self.view_logger)
        self.clicker = Clicker(self.app_identifier,
                               ['images/inventory/inv1.png', 'images/inventory/inv2.png',
                                'images/inventory/inv3.png', 'images/inventory/inv4.png'],
                               ['images/marmur.png']
                               , 720,
                               self.process, self.settingsManager.settings,
                               self.view_logger)
        self.junk_dropper = JunkDropper(self.app_identifier, 'images/bin.jpg', 'images/delete_items.jpg',
                                        'images/bin_opened.JPG',
                                        'images/bin.jpg',
                                        ['images/inventory/inv1.png', 'images/inventory/inv2.png',
                                         'images/inventory/inv3.png', 'images/inventory/inv4.png'],
                                        ['images/to_drop/drobne.png', 'images/to_drop/karas.png',
                                         'images/to_drop/sum.png', 'images/to_drop/lotos.png',
                                         'images/to_drop/pstrag.png', 'images/to_drop/wybielacz.png',
                                         'images/to_drop/rekawica.png', 'images/to_drop/plaszcz.png',
                                         'images/to_drop/pierscien1.png', 'images/to_drop/pierscien2.png',
                                         'images/to_drop/czarna_farba.png', 'images/to_drop/symbol.png',
                                         'images/to_drop/blond_farba.png', 'images/to_drop/czerw_farba.png']
                                        , 2000,
                                        self.process, self.settingsManager.settings,
                                        self.view_logger)
        self.captchaResolver = CaptchaResolver(self.app_identifier,
                                               ["images/captcha/alarm.jpg", "images/captcha/bateria.jpg",
                                                "images/captcha/kura.jpg", "images/captcha/list.jpg",
                                                "images/captcha/piwo.jpg", "images/captcha/rozmowa_w_i.jpg",
                                                "images/captcha/slonce.jpg", "images/captcha/tecza.jpg",
                                                "images/captcha/telefon.jpg", "images/captcha/wysoka.jpg", "images/captcha/deser.jpg"],
                                               ["images/captcha/alarm_label.jpg", "images/captcha/bateria_label.jpg",
                                                "images/captcha/kura_label.jpg", "images/captcha/list_label.jpg",
                                                "images/captcha/piwo_label.jpg", "images/captcha/rozmowa_w_i_label.jpg",
                                                "images/captcha/slonce_label.jpg", "images/captcha/tecza_label.jpg",
                                                "images/captcha/telefon_label.jpg", "images/captcha/wysoka_label.jpg", "images/captcha/deser_label.jpg"],
                                               "images/captcha/captcha.JPG", "images/captcha/tu_klik.jpg", self.process,
                                               self.view_logger)
        self.fish_seller = FishSeller(self.app_identifier, 'images/free_slot.png', self.process,
                                      self.settingsManager.settings, self.view_logger)
        self.threadingManager = ThreadingManager(self.restart)

    def load_settings_from_file(self, path):
        self.settingsManager.load(path)  # run it on button click
        self.view.bait_keys_entry.insert(0, string_list_to_string(self.settingsManager.settings.keys_with_fish_bait))
        if validate_process_name(self.view.scaling_option_menu.get()):
            self.view.switch.configure(state=tkinter.DISABLED)
        # self.view.fishing_base_entry.insert(0, hex(self.settingsManager.settings.fishing_base_address))
        # self.view.fish_caught_base_entry.insert(0, hex(self.settingsManager.settings.fish_is_caught_base_address))
        # self.view.fishing_pole_thrown_offsets_entry.insert(0, offsets_to_hex_string(
        #     self.settingsManager.settings.pole_is_thrown_offsets))
        # self.view.fishing_caught_offsets_entry.insert(0, offsets_to_hex_string(
        #     self.settingsManager.settings.fish_is_caught_offsets))
        # self.view.message_base_entry.insert(0, hex(self.settingsManager.settings.message_base_address))
        # self.view.message_offsets_entry.insert(0, offsets_to_hex_string(
        #     self.settingsManager.settings.message_offsets))
        # self.view.sitting_on_horse_base_entry.insert(0,
        #                                              hex(self.settingsManager.settings.sitting_on_horse_base_address))
        # self.view.sitting_on_horse_offset_entry.insert(0, offsets_to_hex_string(
        #     self.settingsManager.settings.sitting_on_horse_offsets))

    def load_settings(self):
        # if SettingsValidator.validateViewSettings(self.view):
        self.process = self.process.copy(
            Process.get_by_id(displayed_process_name_to_id(self.view.scaling_option_menu.get())))
        # self.settingsManager.settings.fishing_base_address = int(self.view.fishing_base_entry.get(), 16)
        # self.settingsManager.settings.fish_is_caught_base_address = int(self.view.fish_caught_base_entry.get(), 16)
        # self.settingsManager.settings.pole_is_thrown_offsets = \
        #     string_to_int_list(self.view.fishing_pole_thrown_offsets_entry.get())
        # self.settingsManager.settings.fish_is_caught_offsets = \
        #     string_to_int_list(self.view.fishing_caught_offsets_entry.get())
        # self.settingsManager.settings.message_base_address = int(self.view.message_base_entry.get(), 16)
        # self.settingsManager.settings.message_offsets = string_to_int_list(self.view.message_offsets_entry.get())
        # self.settingsManager.settings.sitting_on_horse_base_address = \
        #     int(self.view.sitting_on_horse_base_entry.get(), 16)
        # self.settingsManager.settings.sitting_on_horse_offsets = string_to_int_list(
        #     self.view.sitting_on_horse_offset_entry.get())
        self.settingsManager.settings.keys_with_fish_bait = string_to_string_list(self.view.bait_keys_entry.get())
        self.view.switch.configure(state=tkinter.NORMAL)
        # else:
        #     self.view.switch.configure(state=tkinter.DISABLED)

    def update_logs_box(self, value_to_set):
        self.view.logs_box.configure(state='normal')
        self.view.logs_box.insert("0.0", value_to_set)
        self.view.logs_box.configure(state='disabled')
        return

    def pause_or_resume(self):
        self.load_settings()
        if self.threadingManager.system_pause.is_set() is True:
            logging.info("Pausing...")
            self.threadingManager.system_pause.clear()
        else:
            logging.info("Resuming...")
            self.threadingManager.system_pause.set()

    def reply_to_messages(self):
        if self.bot.message_replier_unpause is True:
            self.bot.message_replier_unpause = False
        else:
            self.bot.message_replier_unpause = True

    def cancel_animation(self):
        if self.bot.cancel_animations is True:
            self.bot.cancel_animations = False
        else:
            self.bot.cancel_animations = True

    def drop_items(self):
        if self.junk_dropper.drop_items is True:
            self.junk_dropper.drop_items = False
        else:
            self.junk_dropper.drop_items = True

    def marble_click(self):
        if self.clicker.click_unpause is True:
            self.clicker.click_unpause = False
        else:
            self.clicker.click_unpause = True

    def sell_items(self):
        if self.fish_seller.sell_items is True:
            self.fish_seller.sell_items = False
        else:
            self.fish_seller.sell_items = True

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
        self.load_settings_from_file(PATH_TO_SETTINGS)
        callable_groups: Dict[str, CallableGroup] = {
            "fish_and_message": CallableGroup(
                tasks=[self.bot.bot_loop, self.bot.message_scanner.message_scan_loop, self.junk_dropper.start_dropping,
                       self.fish_seller.start_selling, self.clicker.click, self.captchaResolver.detect_captcha_loop])}
        self.threadingManager.callable_groups = callable_groups
        self.threadingManager.main_func = self.view.mainloop
        self.threadingManager.start()
