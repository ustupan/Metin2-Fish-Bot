import json
import os
import sys
from typing import List


class Settings:
    def __init__(self, disc):
        self.fishing_base_address: int = disc["fishing_base_address"]
        self.fish_is_caught_base_address: int = disc["fish_is_caught_base_address"]
        self.pole_is_thrown_offsets: List[int] = disc["pole_is_thrown_offsets"]
        self.fish_is_caught_offsets: List[int] = disc["fish_is_caught_offsets"]
        self.message_base_address: int = disc["message_base_address"]
        self.message_offsets: List[int] = disc["message_offsets"]


def _decode(o):
    if isinstance(o, str):
        try:
            return int(o, 16)
        except ValueError:
            return o
    elif isinstance(o, dict):
        return {k: _decode(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_decode(v) for v in o]
    else:
        return o


def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class SettingsLoader:

    def __init__(self):
        self.settings = None

    def load(self):
        with open(resource_path('../../settings/memory_settings.json'), 'r') as f:
            settings_disc = json.load(f, object_hook=_decode)
            self.settings = Settings(settings_disc)
