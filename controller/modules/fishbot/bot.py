import datetime
import logging
import time
import random
from uuid import UUID

import win32event
from controller.internal.logging.view_logger import ViewLogger
from controller.modules.message_replier.message_replier import MessageReplier
from controller.modules.message_scanner.message_scanner import MessageScanner
from controller.managers.operations_manager import OperationsManager
from controller.managers.process_memory_manager import Process
from controller.managers.settings_manager import Settings
from controller.modules.fishbot.fish import Fish

INPUT_KWARGS = {
    'send_to_process': False,
    'focus': True,
    'sleep_between_presses': 0.1,
    'sleep_between_keys': 0.13
}


class Bot:
    def __init__(self, app_id: UUID, process: Process, settings: Settings, logger: ViewLogger):
        self.app_id = app_id
        self.logger = logger
        self.process = process
        self.settings = settings
        self.message_scanner = MessageScanner(self.process, self.settings, ".")
        self.ignore_caught = False
        self.throw_attempts = 0
        self.announced_pole_status = False
        self.cancel_animations = False
        self.last_time_pole_thrown = None
        self.last_message_from_user = None
        self.message_replier = MessageReplier(self.app_id,
                                              'images/wiadomosc.png',
                                              'images/zamknij.png',
                                              self.process, self.logger)
        self.message_replier_unpause = False

    def bot_loop(self):
        mutex_name = self.app_id.hex
        mutex = win32event.CreateMutex(None, False, mutex_name)
        try:
            win32event.WaitForSingleObject(mutex, win32event.INFINITE)
            if not self.pole_is_thrown():
                time.sleep(0.1)
                return self.on_pole_is_not_thrown()
            if self.caught_fish() is True:
                return self.on_fish_is_caught()
            message = self.new_message_received()
            if message[0] and self.message_replier_unpause:
                time.sleep(4)
                self.last_message_from_user = message[1]
                return self.message_replier.reply(message[1])
            else:
                return self.on_pole_is_thrown()
        finally:
            win32event.ReleaseMutex(mutex)

    def on_pole_is_not_thrown(self):
        if self.caught_fish() is True:  # sometimes pole_is_not_thrown is triggered faster than caught_fish
            return self.on_fish_is_caught()
        self.logger.update_logs("Throwing the pole...")
        logging.info("Throwing the pole...")
        self.process.send_input(random.choice(self.settings.keys_with_fish_bait), '1', **INPUT_KWARGS)
        if self.throw_attempts > 30:
            self.logger.update_logs("Too many attempts have been made to "
                                    "throw the pole but none of them were successful. "
                                    "Restart the bot!")
            raise Exception(
                "Too many attempts have been made to throw the pole but none of them were successful.")
        if self.sitting_on_horse() is True:
            self.process.send_input('ctrl+g', **INPUT_KWARGS)
        self.announced_pole_status = False
        self.throw_attempts += 1
        return time.sleep(2.5)

    def on_fish_is_caught(self):
        time.sleep(0.05)  # wait slightly so that we get the msg
        # try to get the timing from chat
        try:
            fish = Fish.parse_chat_message_and_get_fish(self.message_scanner.last_message.content)
        except IndexError:
            fish = Fish.get_by_name('Unknown Fish')

        self.logger.update_logs(f"Caught a(n) {fish.name}!")
        # announce
        logging.info(f"Caught a(n) {fish.name}!")

        # sleep
        OperationsManager.human_sleep(fish.get_timing_to_catch() - 0.05, interval=0.05)

        if self.cancel_animations:
            # pull the pole, then get in and get off the horse to cancel the animation
            self.process.send_input('1', 'ctrl+g', 'ctrl+g', **INPUT_KWARGS)
        else:
            self.process.send_input('1', **INPUT_KWARGS)
        # reset counters
        self.throw_attempts = 0
        self.announced_pole_status = False
        self.last_time_pole_thrown = None
        return time.sleep(2.4)

    def on_pole_is_thrown(self):
        if self.last_time_pole_thrown is None:
            self.last_time_pole_thrown = datetime.datetime.now()
        curr_time = datetime.datetime.now()
        if round((curr_time - self.last_time_pole_thrown).total_seconds()) > 100:
            self.logger.update_logs(f"Throw the pole is stuck. Throwing the pole...")
            logging.info(f"Thrown the pole is stuck. Throwing the pole...")
            self.process.send_input('1', '1', **INPUT_KWARGS)
            self.last_time_pole_thrown = None
        if self.announced_pole_status is False:
            self.logger.update_logs(f"Thrown the pole. Waiting to catch a fish...")
            logging.info(f"Thrown the pole. Waiting to catch a fish...")
            self.announced_pole_status = True

        return time.sleep(0.02)

    def caught_fish(self) -> bool:
        caught_fish_pointer, _ = self.process.read_memory(self.process.base_address +
                                                          self.settings.fish_is_caught_base_address,
                                                          self.settings.fish_is_caught_offsets)
        _, caught_fish_value = self.process.read_memory(caught_fish_pointer, None)

        # # remove after finding address
        # caught_fish_pointer1, _ = self.process.read_memory(self.process.base_address +
        #                                                    21301200,
        #                                                    [456, 1048, 0, 268, 568])
        # _, caught_fish_value1 = self.process.read_memory(caught_fish_pointer1, None)

        return caught_fish_value == 1

    def new_message_received(self):
        message_received_pointer, _ = self.process.read_memory(self.process.base_address +
                                                               self.settings.chat_message_base_address)
        _, message_received_value = self.process.read_memory_string(message_received_pointer, None, string_length=60)

        null_char_position = message_received_value.find('\x00')

        truncated_value = message_received_value[:null_char_position]
        return (self.last_message_from_user != truncated_value and truncated_value is not None and len(
            truncated_value) > 2), truncated_value

    def pole_is_thrown(self) -> bool:
        pole_in_water_timer_pointer, _ = self.process.read_memory(self.process.base_address +
                                                                  self.settings.fishing_base_address,
                                                                  self.settings.pole_is_thrown_offsets)
        _, pole_in_water_timer = self.process.read_memory(pole_in_water_timer_pointer, None)
        logging.info(pole_in_water_timer)
        return pole_in_water_timer != int('0xFFFFFFFF', 16)

    # def pole_is_thrown_invalidate(self) -> bool:  # remove after finding right address
    #     pole_in_water_timer_pointer, _ = self.process.read_memory(self.process.base_address +
    #                                                               21300544,
    #                                                               [260, 0, 28, 916])
    #     _, pole_in_water_timer = self.process.read_memory(pole_in_water_timer_pointer, None)
    #     return pole_in_water_timer != int('0xFFFFFFFF', 16)
    #
    # def pole_is_thrown_invalidate2(self) -> bool:  # remove after finding right address
    #     pole_in_water_timer_pointer, _ = self.process.read_memory(self.process.base_address +
    #                                                               21301200,
    #                                                               [456, 1048, 0, 268, 916])
    #     _, pole_in_water_timer = self.process.read_memory(pole_in_water_timer_pointer, None)
    #     return pole_in_water_timer != int('0xFFFFFFFF', 16)

    def sitting_on_horse(self) -> bool:
        sitting_on_horse_pointer, _ = self.process.read_memory(self.process.base_address +
                                                               self.settings.sitting_on_horse_base_address,
                                                               self.settings.sitting_on_horse_offsets)
        _, sitting_on_horse = self.process.read_memory(sitting_on_horse_pointer, None, True)
        return sitting_on_horse == 1
