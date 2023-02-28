import csv
import logging
from typing import List

FishTimeTypes = [
    [0, 0, 0, 0, 0, 2, 4, 8, 12, 16, 20, 22, 25, 30, 50, 80, 50, 30, 25, 22, 20, 16, 12, 8, 4, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 8, 12, 16, 20, 22, 25, 30, 50, 80, 50, 30, 25, 22, 20],
    [20, 22, 25, 30, 50, 80, 50, 30, 25, 22, 20, 16, 12, 8, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
     100, 100, 100, 100, 100, 100, 100, 100],
    [20, 20, 20, 20, 20, 22, 24, 28, 32, 36, 40, 42, 45, 50, 70, 100, 70, 50, 45, 42, 40, 36, 32, 28, 24, 22, 20, 20,
     20, 20, 20]
]


class Fish:
    # It looks like xxx is on the hook.
    # It looks like xxx is hooked.
    KEYWORDS = [
        'Wygląda na to, że na haczyku jest ',
        'Wyglądało na to, że ',
        ' wisi na haku.'
    ]

    ALIASES = {
        'Purple Hair Dye': 'White Hair Dye'  # hair dyes' timings are the same
    }

    def __init__(self, row: dict):
        self.name = row.get('Name')
        self.time_type_index = int(row.get('Time Type'))

    def get_timing_to_catch(self):
        """Returns the timing in seconds."""
        timings = FishTimeTypes[self.time_type_index]
        best_timing = max(timings)
        best_index = timings.index(best_timing)

        return (best_index * 200 - 99) / 1000

    @classmethod
    def parse_chat_message_and_get_fish(cls, chat_message: str):
        print(chat_message)
        if chat_message.startswith(cls.KEYWORDS[0]):
            for keyword in cls.KEYWORDS:  # strip the fish name
                chat_message = chat_message.replace(keyword, '')

            fish_name = chat_message
            if fish_name in cls.ALIASES.keys():
                fish_name = cls.ALIASES[fish_name]

            return cls.get_by_name(fish_name)

        elif chat_message.startswith('Coś nadziało się na haczyk, '):
            # Something has taken the bait but you can't see what it is.
            # my guess these fish have timing of 1
            return cls.unknown_fish(time_type_index=2)

        else:
            return cls.unknown_fish(time_type_index=0)

    @classmethod
    def get_by_name(cls, fish_name: str):
        for fish in AllFish:
            if fish.name.casefold() == fish_name.casefold():
                return fish

        logging.error(f"Fish with name '{fish_name}' could not be found. Using the default timing...")
        return cls.unknown_fish(time_type_index=0)

    @classmethod
    def unknown_fish(cls, time_type_index: int = 0):
        return cls({'Name': 'Unknown Fish', 'Time Type': time_type_index})


# read fish data
AllFish: List[Fish] = []
with open("settings/fishing.csv", 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file, delimiter=';')
    for _row in reader:
        AllFish.append(Fish(_row))
