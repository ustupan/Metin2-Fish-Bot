import logging
from typing import List

from controller.managers.settings_loader import Settings

POLISH_CHAR_MAPPING = dict([(185, 'ą'), (191, 'ż'), (234, 'ę'), (156, "ś"), (230, "ć"), (163, "Ł"), (179, "ł")])


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
        self.next_message_address = 0xFFFFFFFF

    def message_scan_loop(self):
        logging.debug('Starting')
        self.next_message_address = self.get_message_address()
        msg = self.read_message_at_address(self.next_message_address)
        if self.messages and self.messages[-1] == msg:
            return
        self.messages.append(msg)

    def get_message_address(self) -> int:
        _, next_message_address = self.process.read_memory(self.process.base_address +
                                                           self.settings.message_base_address,
                                                           self.settings.message_offsets)
        return _

    def read_message_at_address(self, address: int) -> Message:
        message = ""
        read_bytes = 0
        while True:
            _, char_as_int = self.process.read_memory(address + read_bytes, None, byte=True)
            if char_as_int in POLISH_CHAR_MAPPING:
                char = POLISH_CHAR_MAPPING[char_as_int]
            else:
                char = chr(char_as_int)
            if char == '\x00':
                content = message.split(".", 1)[0]
                return Message(content=content)

            message += char
            read_bytes += 1
