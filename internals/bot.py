import logging
import time

from internals.game import Game
from managers.loop_manager import Manager
from internals.fish import Fish

INPUT_KWARGS = {
    'send_to_process'      : False,
    'focus'                : True,
    'sleep_between_presses': 0.03,
    'sleep_between_keys'   : 0.06
}


# INPUT_KWARGS = {
#     'send_to_process'      : True,
#     'focus'                : False,
#     'sleep_between_presses': 0.05,
#     'sleep_between_keys'   : 0.1
# }


class Bot:
    def __init__(self):
        self.metin2 = Game()

        self.throw_attempts = 0
        self.announced_pole_status = False

    def bot_loop(self):
        # this method contains the main logic
        if self.metin2.captcha_is_on():
            logging.info("Captcha detected... Please solve it as I don't have the ability to do so, yet.")
            return time.sleep(5.0)

        elif not self.metin2.pole_is_thrown():
            logging.info("Throwing the pole...")
            self.metin2.process.send_input('2', '1', **INPUT_KWARGS)

            # inspect attempt counter
            if self.throw_attempts > 15:
                raise Exception(
                    "Too many attempts have been made to throw the pole but none of them were successful.")

            self.announced_pole_status = False
            self.throw_attempts += 1
            return time.sleep(2.0)

        elif self.metin2.caught_fish() is True:  # if we caught a fish
            time.sleep(0.05)  # wait slightly so that we get the msg
            # try to get the timing from chat
            try:
                fish = Fish.parse_chat_message_and_get_fish(self.metin2.messages[-1].content)
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

        # if the pole is thrown, we just inform and wait
        else:
            if self.announced_pole_status is False:
                logging.info(f"Thrown the pole. Waiting to catch a fish...")
                self.announced_pole_status = True

            return time.sleep(0.02)

    def start(self):
        script = Manager(self.bot_loop, sub_tasks=[self.metin2.message_scan_loop])
        script.start()
        self.metin2.message_scan_loop()
