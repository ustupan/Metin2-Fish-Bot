import logging
import sys

from internals.bot import Bot


def main():
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO, stream=sys.stdout)
    Bot().start()


if __name__ == "__main__":
    main()
