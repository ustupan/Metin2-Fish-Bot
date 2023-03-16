import logging
import sys
import uuid

from controller.app_controller import AppController
from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.managers.settings_manager import SettingsManager
from controller.modules.fish_seller.fish_sell import FishSell
from controller.modules.fish_seller.fish_seller import FishSeller
from controller.modules.junk_dropper.junk_dropper import JunkDropper


def main():
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO, stream=sys.stdout)


if __name__ == "__main__":
    AppController().start()
