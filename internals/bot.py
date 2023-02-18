import logging
import time

from internals.game import Game
from internals.message_scanner import MessageScanner
from internals.settings_loader import SettingsLoader
from managers.loop_manager import Manager
from internals.fish import Fish

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
    def __init__(self):
        self.settingsLoader = SettingsLoader()
        self.settingsLoader.load()
        self.metin2 = Game(self.settingsLoader.settings)
        self.message_scanner = MessageScanner(self.metin2.process, self.settingsLoader.settings)

        self.throw_attempts = 0
        self.announced_pole_status = False

    def bot_loop(self):
        # this method contains the main logic
        if self.metin2.captcha_is_on():
            return self.captcha_detected()

        elif not self.metin2.pole_is_thrown():
            return self.pole_is_not_thrown()

        elif self.metin2.caught_fish() is True:
            return self.fish_is_caught()

        else:
            return self.pole_is_thrown()

    def start(self):
        script = Manager(self.bot_loop, sub_tasks=[self.message_scanner.message_scan_loop])
        script.start()
        self.message_scanner.message_scan_loop()

    @staticmethod
    def captcha_detected():
        logging.info("Captcha detected... Please solve it as I don't have the ability to do so, yet.")
        return time.sleep(5.0)

    def pole_is_not_thrown(self):
        logging.info("Throwing the pole...")
        self.metin2.process.send_input('2', '1', **INPUT_KWARGS)
        # inspect attempt counter
        if self.throw_attempts > 15:
            raise Exception(
                "Too many attempts have been made to throw the pole but none of them were successful.")

        self.announced_pole_status = False
        self.throw_attempts += 1
        return time.sleep(2.0)

    def fish_is_caught(self):
        time.sleep(0.05)  # wait slightly so that we get the msg
        # try to get the timing from chat
        try:
            fish = Fish.parse_chat_message_and_get_fish(self.message_scanner.messages[-1].content)
        except IndexError:
            fish = Fish.get_by_name('Unknown Fish')

        # announce
        logging.info(f"Caught a(n) {fish.name}!")

        # sleep
        Manager.human_sleep(fish.get_timing_to_catch() - 0.05, interval=0.05)

        # pull the pole, then get in and get off the horse to cancel the animation
        self.metin2.process.send_input('1', 'ctrl+g', 'ctrl+g', **INPUT_KWARGS)

        # reset counters
        self.throw_attempts = 0
        self.announced_pole_status = False
        return time.sleep(0.05)

    def pole_is_thrown(self):
        if self.announced_pole_status is False:
            logging.info(f"Thrown the pole. Waiting to catch a fish...")
            self.announced_pole_status = True

        return time.sleep(0.02)
