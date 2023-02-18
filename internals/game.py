from internals.settings_loader import Settings
from managers.process_memory_manager import Process


class Game:
    def __init__(self, memory_settings: Settings):
        self.process = Process.get_by_id(10824)
        self.settings = memory_settings

    def caught_fish(self) -> bool:
        caught_fish_pointer, _ = self.process.read_memory(self.process.base_address +
                                                          self.settings.fishing_base_address,
                                                          self.settings.fish_is_caught_offsets)
        _, caught_fish_value = self.process.read_memory(caught_fish_pointer, None)

        return caught_fish_value == 1

    def pole_is_thrown(self) -> bool:
        pole_in_water_timer_pointer, _ = self.process.read_memory(self.process.base_address +
                                                                  self.settings.fishing_base_address,
                                                                  self.settings.pole_is_thrown_offsets)
        _, pole_in_water_timer = self.process.read_memory(pole_in_water_timer_pointer, None)

        return pole_in_water_timer != int('0xFFFFFFFF', 16)

    def captcha_is_on(self) -> bool:
        captcha_is_on_pointer, _ = self.process.read_memory(self.settings.captcha_window_base_address,
                                                            self.settings.captcha_window_offsets)
        _, captcha_is_on_value = self.process.read_memory(captcha_is_on_pointer, None, byte=True)

        return captcha_is_on_value == 2

    def send_input(self, *args, **kwargs):
        return self.process.send_input(*args, **kwargs)
