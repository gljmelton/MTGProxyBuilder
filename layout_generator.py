import os
import re
import textwrap
import img2pdf
from enum import Enum
from pathlib import Path

from PIL.Image import Image, Resampling

from scryfall import scryfall
from scryfall.card import Card
from pictex import Canvas, Row, Column, Text

from scryfall.scryfall import Scryfall, Faces

WIDTH = 8.5
HEIGHT = 11.0
DPI = 300.0
POINT_SIZE = (DPI / 72.0)

PIXEL_WIDTH = int(WIDTH * DPI)
PIXEL_HEIGHT = int(HEIGHT * DPI)

BIG_SIZES = [18, 14, 12]
REGULAR_SIZES = [12, 9]
SMALL_SIZES = [9, 7]
ONLY_SMALL = [9]
ONLY_TINY = [7]

class Casing(Enum):
    DEFAULT = "Default"
    LOWER = "lower"
    UPPER = "UPPER"

class FontWeight(Enum):
    Bold = 1
    Italic = 2
    Regular = 3

class FontSet:
    def __init__(self, name, regular, bold = None, italic = None, size_multiplier : int = 1):
        self.name = name
        self.regular = regular
        if bold:
            self.bold = bold
        else:
            self.bold = regular

        if italic:
            self.italic = italic
        else:
            self.italic = regular

class LayoutGenerator:
    def __init__(self):
        self.custom_data = {}
        self.card = None

        self.fonts = [
            FontSet("SansSerif", "BeVietnamPro-Regular.ttf"),
            FontSet("Serif", "Alegreya-Regular.ttf"),
            FontSet("Overprint", "Overprint TM.ttf"),
            FontSet("Blackletter", "PirataOne-Regular.ttf"),
            FontSet("Block", "Staatliches-Regular.ttf"),
            FontSet("Monospace", "FiraCode-Regular.ttf"),
            FontSet("Typewriter", "Mom_typewrite.ttf"),
            FontSet("MTG", "Beleren2016-Bold.ttf")
        ]

    def get_fonts(self):
        return self.fonts

    def generate(self, custom_data: dict, card: Card | None) -> bool:
        if card is None:
            print("[LayoutGenerator][generate] Attempting to generate card with no card!")
            return False

        print("[LayoutGenerator][generate] Generating layout...")
        self.custom_data = custom_data
        self.card = card

        return self.generate_card()

    def generate_preview(self) -> bool:
        col = []

        for font in self.fonts:
            col.append(Text(font.name).font_family(rf"fonts\{font.regular}").font_size(64))

        col = Column(*col)

        canvas = Canvas()
        canvas.size(600, 800)
        canvas.background_color("white")
        img = canvas.render(col).to_pillow()
        img.save("font_preview.png", "PNG", resolution=100.0)

        return True


    def generate_card(self) -> bool:
        print("[LayoutGenerator][generate_card] Generating card...")
        fonts = [
            self.get_font_for_name(self.custom_data["style1"]),
            self.get_font_for_name(self.custom_data["style2"]),
            self.get_font_for_name(self.custom_data["style3"]),
        ]

        #Col Main Page
        col = []
        #Name
        if self.custom_data["nickname"] == "":
            col.append(self.generate_data_row(self.format_name(Scryfall.get_card_name(self.card)), fonts, BIG_SIZES, FontWeight.Bold))
        else:
            col.append(self.generate_data_row(self.format_name(self.custom_data["nickname"]), fonts, BIG_SIZES, FontWeight.Bold))
            col.append(self.generate_data_row(self.format_name(Scryfall.get_card_name(self.card)), fonts, SMALL_SIZES, FontWeight.Italic))

        #Type
        col.append(self.generate_data_row(self.format_type_line(Scryfall.get_type_line(self.card)), fonts, REGULAR_SIZES, FontWeight.Regular))

        #Oracle
        oracle_sizes = REGULAR_SIZES
        if len(Scryfall.get_card_oracle(self.card)) > 250:
            oracle_sizes = ONLY_TINY
        if self.card.type_line == "Dungeon":
            col.append(self.generate_data_row(
                self.format_oracle(Scryfall.get_card_oracle(self.card, Faces.Front)),  # Wrap text and remove any reminder text
                fonts, ONLY_SMALL, FontWeight.Regular))
        else:
            col.append(self.generate_data_row(
                self.format_oracle(Scryfall.get_card_oracle(self.card, Faces.Front)), #Wrap text and remove any reminder text
                fonts, oracle_sizes, FontWeight.Regular))

        row = []
        #Mana Value
        if Scryfall.get_mana_value(self.card):
            row.append(self.generate_data_row(self.format_mana(Scryfall.get_mana_value(self.card)), fonts, REGULAR_SIZES,
                                       FontWeight.Regular))
        #Power/Toughness
        if Scryfall.get_power(self.card, Faces.Front) and Scryfall.get_toughness(self.card, Faces.Front):
            power = Scryfall.get_power(self.card, Faces.Front)
            if not self.custom_data["power"] == "":
                power = self.custom_data["power"]

            toughness = Scryfall.get_toughness(self.card, Faces.Front)
            if not self.custom_data["toughness"] == "":
                toughness = self.custom_data["toughness"]

            row.append(self.generate_data_row(f"{power}/{toughness}", fonts, REGULAR_SIZES, FontWeight.Regular))


        col = Column(
            *col,
            Row(*row)
        )
        col.padding(0.15 * DPI)

        canvas = Canvas()
        canvas.size(PIXEL_WIDTH, PIXEL_HEIGHT)
        canvas.background_color("white")
        img = canvas.render(col).to_pillow().convert("RGB")

        #img = img.resize((int(img.size[0] / 3), int(img.size[1] / 3)), Resampling.LANCZOS)
        pdf_path = rf"output\{Scryfall.get_card_name(self.card)}.pdf"
        img.save(rf"output\{Scryfall.get_card_name(self.card)}.png", "PNG")

        try:
            layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))
            Path(pdf_path).write_bytes(img2pdf.convert(rf"output\{Scryfall.get_card_name(self.card)}.png", layout_fun=layout))
            #img.save(pdf_path, "PDF",resolution=100.0, save_all=True)
            os.startfile(rf"{pdf_path}")
            return True
        except PermissionError:
            print(f"[LayoutGenerator][generate_card] Permission error!")
            return False

    def generate_data_row(self, text, fonts, sizes, weight):
        row = []
        print(f"Generating row data for {text}")
        for font in fonts:
            print(f"At font {font.name}")
            row.append(self.generate_data_column(text, font, sizes, weight))

        return Row(*row)

    def generate_data_column(self, text, font, sizes, weight):
        column = []
        print (f"Generating column data for font {font.name}")
        for size in sizes:
            print(f"At size {size}")
            column.append(self.generate_data_set(text, font, size, weight))

        return Column(*column)

    def generate_data_set(self, text, font : FontSet, size, weight : FontWeight):
        print(f"Generating data for font {font.name}")
        if size >= 14:
            text = self.wrap_text(18, text)
        font = self.get_weight_for_font(font, weight)
        regular = Text(text)
        self.style_text(regular, font, size)

        invert = Text(text)
        self.style_text(invert, font, size, True)

        return Column(regular, invert)

    def get_weight_for_font(self, font : FontSet, weight):
        if weight == FontWeight.Bold:
            return font.bold
        if weight == FontWeight.Italic:
            return font.italic

        return font.regular

    def style_text(self, text: Text, font, size, invert=False):
        text.font_family(rf"fonts\{font}").font_size(size*POINT_SIZE).color("black").margin(0.05*DPI)
        if invert:
            text.background_color("black")
            text.padding(0.05 * DPI)
            text.color("white")

        else:
            text.background_color("white")
            text.color("black")

    def get_font_for_name(self, name):
        for font in self.fonts:
            if font.name == name:
                return font

        return None

    def get_power(self):
        if self.custom_data["power"]:
            return self.custom_data["power"]

        return self.card.power

    def get_toughness(self):
        if self.custom_data["toughness"]:
            return self.custom_data["toughness"]

        return self.card.toughness

    def wrap_text(self, width: int, text: str):
        return '\n\n'.join(['\n'.join(textwrap.wrap(line, width,
                 break_long_words=False, replace_whitespace=False))
                 for line in text.splitlines() if line.strip() != ''])

    def format_name(self, text: str):
        return text

    def format_type_line(self, text: str):
        if len(text) > 20:
            text = text.replace(" \u2014 ", "\n")
        return text

    def format_mana(self, text: str):
        return text.replace("{", "").replace("}", "")

    def format_oracle(self, text: str):
        text = self.remove_parenthenticals(text)
        text = text.replace("{", "").replace("}", "")
        text = self.wrap_text(34, text)
        if self.card.type_line == "Dungeon":
            print("Formatting dungeon")
            text = text.replace(" \u2014 ", "\n")
        return text

    def remove_parenthenticals(self, text: str):
        return re.sub("[\\(\\[].*?[\\)\\]]", "", text)