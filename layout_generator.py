import os

from scryfall.card import Card
from pictex import Canvas, Row, Column, Text, Image
import textwrap
from PIL import Image as PILImage

WIDTH = 8.5
HEIGHT = 11.0
DPI = 300.0
POINT_SIZE = (DPI / 72.0)

PIXEL_WIDTH = int(WIDTH * DPI)
PIXEL_HEIGHT = int(HEIGHT * DPI)

DEFAULT_WEIGHT = 9
MICRO_WEIGHT = int(7.5)

class Style:
    def __init__(self,
            default_font: str,
            bold_font: str,
            italic_font: str,
            title_weight: int = DEFAULT_WEIGHT,
            normal_weight: int = DEFAULT_WEIGHT,
            small_weight: int = MICRO_WEIGHT):
        self.default_font = default_font

        if bold_font:
            self.bold_font = bold_font
        else:
            self.bold_font = self.default_font

        if italic_font:
            self.italic_font = italic_font
        else:
            self.italic_font = self.default_font

        self.title_weight = title_weight * POINT_SIZE
        self.normal_weight = normal_weight * POINT_SIZE
        self.small_weight = small_weight * POINT_SIZE

class LayoutGenerator:

    def __init__(self):
        self.custom_data = {}
        self.card = None

    def generate(self, custom_data: dict, card: Card | None):
        if card is None:
            print("[LayoutGenerator][generate] Attempting to generate card with no card!")
            return

        print("[LayoutGenerator][generate] Generating layout...")
        self.custom_data = custom_data
        self.card = card

        self.generate_card()

    def generate_card(self):
        print("[LayoutGenerator][generate_card] Generating card...")
        nickname = ""
        if self.custom_data["nickname"]:
            nickname = Text(self.custom_data["nickname"])
            self.format_text(nickname)

        name = Text(self.card.name)
        self.format_text(name)

        c_type = Text(self.card.type_line)
        self.format_text(c_type)

        oracle = Text(self.wrap_text(36, self.card.oracle_text))
        self.format_text(oracle)

        pt = ""
        if self.card.power and self.card.toughness:
            pt = Text(f"{self.get_power()}/{self.get_toughness()}")
            self.format_text(pt)

        #Col Main Page
        col = Column(
            #Row 1 - Names
            Row(
                name,
            nickname,
            ),
            #Row 2 - Type line
            Row(
                c_type
            ),
            #Row 3 - Oracle text
            Row(
                oracle
            ),
            #Row 4 - P/T and other info
            Row(
                pt
            )
        )
        col.padding(0.25 * DPI)

        canvas = Canvas()
        canvas.size(PIXEL_WIDTH, PIXEL_HEIGHT)
        canvas.background_color("white")
        img = canvas.render(col).to_pillow()

        pdf_path = f"{self.card.name}.pdf"
        img.save(pdf_path, "PDF",resolution=100.0, save_all=True)
        os.startfile(pdf_path)

    def get_power(self):
        if self.custom_data["power"]:
            return self.custom_data["power"]

        return self.card.power

    def get_toughness(self):
        if self.custom_data["toughness"]:
            return self.custom_data["toughness"]

        return self.card.toughness

    def wrap_text(self, width: int, text: str):
        return '\n'.join(['\n'.join(textwrap.wrap(line, width,
                 break_long_words=False, replace_whitespace=False))
                 for line in text.splitlines() if line.strip() != ''])

    @staticmethod
    def format_text(text: Text):
        text.font_size(DEFAULT_WEIGHT * POINT_SIZE)
        text.font_family("fonts/CloisterBlack.ttf")
        text.color("black")
        text.margin(15)
        text.line_height(1.2)