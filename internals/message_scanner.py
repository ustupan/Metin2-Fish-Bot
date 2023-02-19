import logging
import time
from typing import List

from internals.settings_loader import Settings


class Message:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content


class MessageScanner:
    def __init__(self, process, memory_settings: Settings):
        self.process = process
        self.settings = memory_settings
        self.messages: List[Message] = list()
        self.last_message_counter = -1
        self.next_message_address = 0xFFFFFFFF

    def message_scan_loop(self):
        """Trust me, this algorithm can't be any simpler."""
        time.sleep(0.01)  # small sleep to not hog the cpu
        if self.last_message_counter < self.settings.message_cache_size:  # if the cache isn't full
            cached_message_counter = self.get_cached_message_counter()
            # sometimes after going back to character selection, this counter continues to increment
            # in that case, get the remainder
            if cached_message_counter > self.settings.message_cache_size:
                cached_message_counter %= self.settings.message_cache_size

            # if there isn't any new message, return
            if cached_message_counter == self.last_message_counter:
                return

            # after "MESSAGE_CACHE_SIZE" messages, Metin2 starts removing older messages (a queue)
            # then we use another address to learn where the new message will be placed
            if cached_message_counter == self.settings.message_cache_size:
                self.next_message_address = self.get_next_message_address()

                # if we started scanning after the cache was full, return
                if self.last_message_counter == self.settings.message_cache_size:
                    self.last_message_counter = cached_message_counter
                    return

            self.last_message_counter = cached_message_counter
            current_message_address = self.get_current_message_address(cached_message_counter)

        else:  # if the cache is full
            current_message_address = self.next_message_address
            self.next_message_address = self.get_next_message_address()

            # if the cache is full and we don't have the address of the recently rewritten pointer, return
            if current_message_address == 0xFFFFFFFF:
                return

            # if there isn't any new message, continue
            if current_message_address == self.next_message_address:
                return

        self.read_and_save_message(current_message_address)

    def get_cached_message_counter(self) -> int:
        return self.process.read_memory(self.process.base_address + self.settings.chat_base_address +
                                        self.settings.message_cache_counter_offsets[0], None)[1]

    def get_current_message_address(self, cached_message_counter):
        return self.process.read_memory(self.process.base_address + self.settings.chat_base_address,
                                        [(cached_message_counter - 1) * 0x4] +
                                        self.settings.message_content_offsets)[0]

    def get_next_message_address(self) -> int:
        _, next_message_address = self.process.read_memory(self.process.base_address +
                                                           self.settings.next_message_base_address,
                                                           [0] + self.settings.message_content_offsets)
        return _

    def read_and_save_message(self, current_message_address):
        msg = self.read_message_at_address(current_message_address)
        logging.debug(f"New in-game message: {msg.content}")
        self.messages.append(msg)

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
