import logging
import time

from controller.modules.message_scanner.message_scanner import MessageScanner
from controller.managers.operations_manager import OperationsManager
from controller.managers.process_memory_manager import Process
from controller.managers.settings_manager import Settings
from controller.modules.fishbot.fish import Fish

INPUT_KWARGS = {
    'send_to_process': False,
    'focus': True,
    'sleep_between_presses': 0.03,
    'sleep_between_keys': 0.06
}


# INPUT_KWARGS = {
#     'send_to_process'      : True,
#     'focus'                : False,
#     'sleep_between_presses': 0.05,
#     'sleep_between_keys'   : 0.1
# }


class Bot:
    def __init__(self, process: Process, settings: Settings):
        self.process = process
        self.settings = settings
        self.message_scanner = MessageScanner(self.process, self.settings, ".")
        self.throw_attempts = 0
        self.announced_pole_status = False

    def bot_loop(self):
        if not self.pole_is_thrown():
            return self.on_pole_is_not_thrown()

        if self.caught_fish() is True:
            return self.on_fish_is_caught()

        else:
            return self.on_pole_is_thrown()

    def on_pole_is_not_thrown(self):
        time.sleep(0.05)
        if self.caught_fish() is True:  # sometimes pole_is_not_thrown is triggered faster than caught_fish
            return self.on_fish_is_caught()

        logging.info("Throwing the pole...")
        self.process.send_input('2', '1', **INPUT_KWARGS)
        # inspect attempt counter
        if self.throw_attempts > 15:
            raise Exception(
                "Too many attempts have been made to throw the pole but none of them were successful.")

        self.announced_pole_status = False
        self.throw_attempts += 1
        return time.sleep(2.0)

    def on_fish_is_caught(self):
        time.sleep(0.05)  # wait slightly so that we get the msg
        # try to get the timing from chat
        try:
            fish = Fish.parse_chat_message_and_get_fish(self.message_scanner.messages[-1].content)
        except IndexError:
            fish = Fish.get_by_name('Unknown Fish')

        # announce
        logging.info(f"Caught a(n) {fish.name}!")

        # sleep
        OperationsManager.human_sleep(fish.get_timing_to_catch() - 0.05, interval=0.05)

        # pull the pole, then get in and get off the horse to cancel the animation
        self.process.send_input('1', 'ctrl+g', 'ctrl+g', **INPUT_KWARGS)

        # reset counters
        self.throw_attempts = 0
        self.announced_pole_status = False
        return time.sleep(0.05)

    def on_pole_is_thrown(self):
        if self.announced_pole_status is False:
            logging.info(f"Thrown the pole. Waiting to catch a fish...")
            self.announced_pole_status = True

        return time.sleep(0.02)

    def caught_fish(self) -> bool:
        caught_fish_pointer, _ = self.process.read_memory(self.process.base_address +
                                                          self.settings.fish_is_caught_base_address,
                                                          self.settings.fish_is_caught_offsets)
        _, caught_fish_value = self.process.read_memory(caught_fish_pointer, None)

        return caught_fish_value == 1

    def pole_is_thrown(self) -> bool:
        pole_in_water_timer_pointer, _ = self.process.read_memory(self.process.base_address +
                                                                  self.settings.fishing_base_address,
                                                                  self.settings.pole_is_thrown_offsets)
        _, pole_in_water_timer = self.process.read_memory(pole_in_water_timer_pointer, None)
        return pole_in_water_timer != int('0xFFFFFFFF', 16)
