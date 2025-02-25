import json
import os
import sys
from typing import List


class Settings:
    def __init__(self):
        self.keys_with_fish_bait: List[str] = ['2']
        self.fishing_base_address: int = 0
        self.fish_is_caught_base_address: int = 0
        self.pole_is_thrown_offsets: List[int] = [0]
        self.fish_is_caught_offsets: List[int] = [0]
        self.message_base_address: int = 0
        self.message_offsets: List[int] = [0]
        self.sitting_on_horse_base_address: int = 0
        self.sitting_on_horse_offsets: List[int] = [0]

    def load(self, disc):
        self.keys_with_fish_bait: List[str] = disc["keys_with_fish_bait"]
        self.fishing_base_address: int = disc["fishing_base_address"]
        self.fish_is_caught_base_address: int = disc["fish_is_caught_base_address"]
        self.pole_is_thrown_offsets: List[int] = disc["pole_is_thrown_offsets"]
        self.fish_is_caught_offsets: List[int] = disc["fish_is_caught_offsets"]
        self.message_base_address: int = disc["message_base_address"]
        self.message_offsets: List[int] = disc["message_offsets"]
        self.sitting_on_horse_base_address: int = disc["sitting_on_horse_base_address"]
        self.sitting_on_horse_offsets: List[int] = disc["sitting_on_horse_offsets"]
        return self


def _decode(o):
    if isinstance(o, str):
        if is_hex(o):
            try:
                return int(o, 16)
            except ValueError:
                return o
        return o
    elif isinstance(o, dict):
        return {k: _decode(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_decode(v) for v in o]
    else:
        return o


def is_hex(string):
    str_string = str(string)  # Convert input to a string
    if str_string.find("0x") != -1:
        return True
    else:
        return False


def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class SettingsManager:

    def __init__(self):
        self.settings: Settings = Settings()

    def load(self, path):
        with open(resource_path(path), 'r') as f:
            settings_disc = json.load(f, object_hook=_decode)
            self.settings = self.settings.load(settings_disc)
