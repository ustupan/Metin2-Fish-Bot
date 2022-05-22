import math
import random
import string

from PIL import Image, ImageDraw, ImageFont

# general
IMAGE_SIZE = (80, 34)
UPSCALE_MULTIPLIER = 1
DOWNSCALE_MULTIPLIER = 1
IMAGE_MODE = 'RGB'

# text
TEXT_COLOR = 0xFFFFFFFF
TEXT_LENGTH = 5
TEXT_SIZE = 32
TEXT_FONT = ImageFont.truetype('fs-tahoma-8px.ttf', size=int(TEXT_SIZE * UPSCALE_MULTIPLIER))
POSSIBLE_LETTERS = string.ascii_uppercase + string.digits

# background
BACKGROUND_COLOR = 0x000000
LINE_COUNT = 6
LINE_WIDTH = 1
POSSIBLE_LINE_COLORS = [
    0x710071,  # pink
    0x818100,  # yellow
    0xff0404,  # red
    0x00007a,  # blue
    0x007171,  # cyan
    0x006800,  # green
    0x7d7d7d,  # white
]
MAX_LINE_LENGTH = 50
MIN_LINE_LENGTH = 15
ANGLE_STEP = 3


class CaptchaGenerator:
    def __init__(self, word: str = None):
        self.word = word or "".join(random.choices(POSSIBLE_LETTERS, k=TEXT_LENGTH))

        self.img = Image.new(mode=IMAGE_MODE,
                             size=(
                                 int(IMAGE_SIZE[0] * UPSCALE_MULTIPLIER),
                                 int(IMAGE_SIZE[1] * UPSCALE_MULTIPLIER)),
                             color=BACKGROUND_COLOR)

        self.draw = ImageDraw.Draw(self.img)

        self.draw_lines()
        self.draw_text()

        self.img.show()
        self.downscale(DOWNSCALE_MULTIPLIER)
        self.upscale(DOWNSCALE_MULTIPLIER)

    def draw_text(self):
        x, y = self.draw.textsize(self.word, font=TEXT_FONT)
        self.draw.text(
            xy=((self.img.width - x) / 2,
                (self.img.height - y) / 2),
            text=self.word, fill=0xFFFFFFFF, font=TEXT_FONT)

    def draw_lines(self):
        for i in range(LINE_COUNT):
            random_starting_point = (random.randint(0, self.img.width), random.randint(0, self.img.height))

            random_length = random.randint(
                int(MIN_LINE_LENGTH * UPSCALE_MULTIPLIER),
                int(MAX_LINE_LENGTH * UPSCALE_MULTIPLIER))

            possible_end_points = []
            for angle in random.sample(range(0, 360, ANGLE_STEP), k=int(360 / ANGLE_STEP)):
                possible_end_points.append((
                    int(random_starting_point[0] + random_length * math.cos(angle)),
                    int(random_starting_point[1] + random_length * math.sin(angle))
                ))

            # filter
            filtered_end_points = []
            for end_point in possible_end_points:
                # if its in visible area
                if 0 <= end_point[0] <= self.img.width and 0 <= end_point[1] <= self.img.height:
                    if end_point not in filtered_end_points:  # if not a duplicate
                        filtered_end_points.append(end_point)

            self.draw.line(
                xy=(random_starting_point, random.choice(filtered_end_points)),
                fill=random.choice(POSSIBLE_LINE_COLORS),
                width=int(LINE_WIDTH * UPSCALE_MULTIPLIER))

    def downscale(self, multiplier: int):
        self.img.thumbnail(
            size=(int(self.img.width / multiplier),
                  int(self.img.height / multiplier))
        )

    def upscale(self, multiplier: int):
        self.img = self.img.resize(
            size=(int(self.img.width * multiplier),
                  int(self.img.height * multiplier))
        )


captcha = CaptchaGenerator("LF84F")
captcha.img.show()
