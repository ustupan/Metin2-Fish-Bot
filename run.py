import logging
import sys

from controller.app_controller import AppController


def main():
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO, stream=sys.stdout)


if __name__ == "__main__":
    AppController().start()