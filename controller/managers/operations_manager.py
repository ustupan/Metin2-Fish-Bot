import random
import time
import keyboard


class OperationsManager:

    @staticmethod
    def human_sleep(length: float, interval: float = None):
        # 10% inconsistency
        interval = interval or length / 10
        time.sleep(random.uniform(length - interval, length + interval))

    @staticmethod
    def press_and_release(button: str,
                          sleep_before: float = 0,
                          sleep_between: float = 0,
                          sleep_after: float = 0,
                          precise: bool = False):
        if precise is True:
            sleep = time.sleep
        else:
            sleep = OperationsManager.human_sleep

        sleep(sleep_before)
        keyboard.press(button)
        sleep(sleep_between)
        keyboard.release(button)
        sleep(sleep_after)
