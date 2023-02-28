from customtkinter import CTkEntry

from view.app import App


def string_to_int_list(string):
    return [int(x, 16) for x in string[1:-1].split(",")]


class SettingsValidator:

    @staticmethod
    def validateViewSettings(view: App):
        settings_are_valid = []
        settings_are_valid.append(SettingsValidator.validateEntryInt(view.fishing_base_entry))
        settings_are_valid.append(SettingsValidator.validateEntryInt(view.fish_caught_base_entry))
        settings_are_valid.append(settings_are_valid and SettingsValidator.
                                  validateEntryIntList(view.fishing_pole_thrown_offsets_entry))
        settings_are_valid.append(SettingsValidator.
                                  validateEntryIntList(view.fishing_caught_offsets_entry))
        settings_are_valid.append(SettingsValidator.validateEntryInt(view.message_base_entry))
        settings_are_valid.append(SettingsValidator.validateEntryIntList(view.message_offsets_entry))
        return all(settings_are_valid)

    @staticmethod
    def validateEntryInt(entry: CTkEntry):
        try:
            int(entry.get(), 16)
            entry.configure(border_color="green")
            return True
        except ValueError:
            entry.configure(border_color="red")
            return False

    @staticmethod
    def validateEntryIntList(entry: CTkEntry):
        try:
            string_to_int_list(entry.get())
            entry.configure(border_color="green")
            return True
        except ValueError:
            entry.configure(border_color="red")
            return False
