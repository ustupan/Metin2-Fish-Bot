import logging
from typing import List

from controller.managers.settings_manager import Settings
import time

POLISH_CHAR_MAPPING = dict([(185, 'ą'), (191, 'ż'), (234, 'ę'), (156, "ś"), (230, "ć"), (163, "Ł"), (179, "ł")])


class Message:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content


class MessageScanner:
    def __init__(self, process, settings: Settings, end_of_content_char: chr = ""):
        self.last_message = None
        self.process = process
        self.settings = settings
        self.next_message_address = 0xFFFFFFFF
        self.end_of_content_char = end_of_content_char
        self.messages_content = []

    def message_scan_loop(self):
        logging.debug('Starting')
        self.next_message_address = self.get_message_address()
        msg = self.read_message_at_address(self.next_message_address, self.end_of_content_char)
        self.last_message = msg
        time.sleep(0.01)

    def get_message_address(self) -> int:
        _, next_message_address = self.process.read_memory(self.process.base_address +
                                                           self.settings.message_base_address,
                                                           self.settings.message_offsets)
        return _

    def read_message_at_address(self, address: int, end_of_content_char: chr = "") -> Message:
        message = ""
        read_bytes = 0
        while True:
            _, char_as_int = self.process.read_memory(address + read_bytes, None, byte=True)
            if char_as_int in POLISH_CHAR_MAPPING:
                char = POLISH_CHAR_MAPPING[char_as_int]
            else:
                char = chr(char_as_int)
            if char == '\x00':
                content = message.split(end_of_content_char, 1)[0]
                return Message(content=content)

            message += char
            read_bytes += 1
