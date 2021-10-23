import logging
import time
from typing import List

from managers.process_memory_manager import Process

# fishing addresses
BASE_ADDRESS = 0x006EF5F0
POLE_IS_THROWN_OFFSETS = [0x0, 0x79C]
FISH_IS_CAUGHT_OFFSETS = [0x0, 0x844]

# captcha stuff
CAPTCHA_WINDOW_BASE_ADDRESS = 0x00774B68  # or 0x006F6CFC
CAPTCHA_WINDOW_OFFSETS = [0x54]
CAPTCHA_IMAGE_SIZE = (80, 34)

# chat stuff
CHAT_BASE_ADDRESS = 0x006EF65C
MESSAGE_CONTENT_OFFSETS = [0x60, 0x0]
MESSAGE_CACHE_COUNTER_OFFSET = [0x1C]
MESSAGE_CACHE_SIZE = 301
# next message address after 300 messages
NEXT_MESSAGE_BASE_ADDRESS = 0x006EF668
NEXT_MESSAGE_OFFSET = [0x0]


def int_to_str(_int: int):
    """Converts 4 byte integers to str"""
    # convert to hex first
    _hex = '{:<08X}'.format(_int)

    for i in range(0, len(_hex), 2):
        __hex = _hex[i:i + 2]
        if __hex == '00' or __hex == 'FF':
            _hex = _hex[:i]
            break

    # then convert to ascii and return
    # return _int.to_bytes((_int.bit_length() + 7) // 8, 'big').decode()
    return bytes.fromhex(_hex).decode('latin_1')[::-1]


class Message:
    def __init__(self, content: str):
        self.content = content
        # self.sent_date = sent_date

    def __str__(self):
        return self.content


class Game:
    def __init__(self):
        self.process = Process.get_by_name("metin2client.exe", 'Mt2 Classic')

        # fishing
        self.fishing_base_address = self.process.base_address + BASE_ADDRESS
        # captcha
        self.captcha_base_address = self.process.base_address + CAPTCHA_WINDOW_BASE_ADDRESS
        # chat
        self.chat_base_address = self.process.base_address + CHAT_BASE_ADDRESS
        self.next_message_base_address = self.process.base_address + NEXT_MESSAGE_BASE_ADDRESS

        self.messages: List[Message] = list()
        self.last_message_counter = -1
        self.next_message_address = 0xFFFFFFFF

    def caught_fish(self) -> bool:
        caught_fish_pointer, _ = self.process.read_memory(self.fishing_base_address, FISH_IS_CAUGHT_OFFSETS)
        _, caught_fish_value = self.process.read_memory(caught_fish_pointer, None)

        return caught_fish_value == 1

    def pole_is_thrown(self) -> bool:
        pole_in_water_timer_pointer, _ = self.process.read_memory(self.fishing_base_address, POLE_IS_THROWN_OFFSETS)
        _, pole_in_water_timer = self.process.read_memory(pole_in_water_timer_pointer, None)

        return pole_in_water_timer != int('0xFFFFFFFF', 16)

    def captcha_is_on(self) -> bool:
        captcha_is_on_pointer, _ = self.process.read_memory(self.captcha_base_address, CAPTCHA_WINDOW_OFFSETS)
        _, captcha_is_on_value = self.process.read_memory(captcha_is_on_pointer, None, byte=True)

        return captcha_is_on_value == 2

    def get_cached_message_counter(self) -> int:
        return self.process.read_memory(self.chat_base_address + MESSAGE_CACHE_COUNTER_OFFSET[0], None)[1]

    def get_next_message_address(self) -> int:
        _, next_message_address = self.process.read_memory(self.next_message_base_address,
                                                           [0] + MESSAGE_CONTENT_OFFSETS)

        return _

    def read_message_at_address(self, address: int) -> Message:
        message = ""
        read_bytes = 0
        while True:
            _, char_as_int = self.process.read_memory(address + read_bytes, None, byte=True)

            char = chr(char_as_int)
            if char == '\x00':
                return Message(content=message)

            message += char
            read_bytes += 1

    def message_scan_loop(self):
        """Trust me, this algorithm can't be any simpler."""
        time.sleep(0.01)  # small sleep to not hog the cpu

        if self.last_message_counter < MESSAGE_CACHE_SIZE:  # if the cache isn't full
            cached_message_counter = self.get_cached_message_counter()

            # sometimes after going back to character selection, this counter continues to increment
            # in that case, get the remainder
            if cached_message_counter > MESSAGE_CACHE_SIZE:
                cached_message_counter %= MESSAGE_CACHE_SIZE

            # if there isn't any new message, return
            if cached_message_counter == self.last_message_counter:
                return

            # after "MESSAGE_CACHE_SIZE" messages, Metin2 starts removing older messages (a queue)
            # then we use another address to learn where the new message will be placed
            if cached_message_counter == MESSAGE_CACHE_SIZE:
                self.next_message_address = self.get_next_message_address()

                # if we started scanning after the cache was full, return
                if self.last_message_counter == MESSAGE_CACHE_SIZE:
                    self.last_message_counter = cached_message_counter
                    return

            self.last_message_counter = cached_message_counter
            current_message_address = \
                self.process.read_memory(self.chat_base_address,
                                         [(cached_message_counter - 1) * 0x4] + MESSAGE_CONTENT_OFFSETS)[0]
        else:  # if the cache is full
            current_message_address = self.next_message_address
            self.next_message_address = self.get_next_message_address()

            # if the cache is full and we don't have the address of the recently rewritten pointer, return
            if current_message_address == 0xFFFFFFFF:
                return

            # if there isn't any new message, continue
            if current_message_address == self.next_message_address:
                return

        msg = self.read_message_at_address(current_message_address)
        logging.debug(f"New in-game message: {msg.content}")
        self.messages.append(msg)

    def send_input(self, *args, **kwargs):
        return self.process.send_input(*args, **kwargs)
