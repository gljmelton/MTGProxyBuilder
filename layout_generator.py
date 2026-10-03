import os
import re
import textwrap
from typing import Tuple

import img2pdf
from enum import Enum
from pathlib import Path
from scryfall.card import Card
from pictex import Canvas, Row, Column, Text, Shadow, TextAlign, LinearGradient
from scryfall.scryfall import Scryfall, Faces, Layout


MANA_WHITE = "#f0f2c0"
MANA_BLUE = "#b5cde3"
MANA_BLACK = "#aca29a"
MANA_RED = "#db8664"
MANA_GREEN = "#93b483"
MANA_GENERIC = "#beb9b2"
SYMBOL_COLOR = "#111"
SYMBOL_FONT = "fonts/mana.ttf"
TEXT_FONT = "fonts/mplantin.ttf"
SYMBOL_SIZE = 28
SPLIT_SYMBOL_OFFSET = 14
ICON_MARGIN = 10

class ColorSymbols(Enum):
    WHITE = "\ue600"
    BLUE = "\ue601"
    BLACK = "\ue602"
    RED = "\ue603"
    GREEN = "\ue604"
    COLORLESS = "\ue904"

class GenericSymbols(Enum):
    ZERO = "\ue605"
    ONE = "\ue606"
    TWO = "\ue607"
    THREE = "\ue608"
    FOUR = "\ue609"
    FIVE = "\ue60a"
    SIX = "\ue60b"
    SEVEN = "\ue60c"
    EIGHT = "\ue60d"
    NINE = "\ue60e"
    TEN = "\ue60f"
    ELEVEN = "\ue610"
    TWELVE = "\ue611"
    THIRTEEN = "\ue612"
    FOURTEEN = "\ue613"
    FIFTEEN = "\ue614"
    SIXTEEN = "\ue62a"
    SEVENTEEN = "\ue62b"
    EIGHTEEN = "\ue62c"
    NINETEEN = "\ue62d"
    TWENTY = "\ue62e"
    X = "\ue615"

class TapSymbols(Enum):
    TAP = "\ue61a"
    UNTAP = "\ue61b"
    OLD_TAP = "\ue61c"

class SpecialSymbols(Enum):
    MDFC_FRONT = "\ue9d3"
    MDFC_BACK = "\ue9d4"
    LOYALTY = "\ue628" # "\ue628"

class SplitSymbols(Enum):
    MANA_WU = ((ColorSymbols.WHITE, MANA_WHITE), (ColorSymbols.BLUE, MANA_BLUE))
    MANA_WB = ((ColorSymbols.WHITE, MANA_WHITE), (ColorSymbols.BLACK, MANA_BLACK))
    MANA_UB = ((ColorSymbols.BLUE, MANA_BLUE), (ColorSymbols.BLACK, MANA_BLACK))
    MANA_UR = ((ColorSymbols.BLUE, MANA_BLUE), (ColorSymbols.RED, MANA_RED))
    MANA_BR = ((ColorSymbols.BLACK, MANA_BLACK), (ColorSymbols.RED, MANA_RED))
    MANA_BG = ((ColorSymbols.BLACK, MANA_BLACK), (ColorSymbols.GREEN, MANA_GREEN))
    MANA_RW = ((ColorSymbols.RED, MANA_RED), (ColorSymbols.WHITE, MANA_WHITE))
    MANA_RG = ((ColorSymbols.RED, MANA_RED), (ColorSymbols.GREEN, MANA_GREEN))
    MANA_GW = ((ColorSymbols.GREEN, MANA_GREEN), (ColorSymbols.WHITE, MANA_WHITE))
    MANA_GU = ((ColorSymbols.GREEN, MANA_GREEN), (ColorSymbols.BLUE, MANA_BLUE))
    MANA_CW = ((ColorSymbols.COLORLESS, MANA_GENERIC), (ColorSymbols.WHITE, MANA_WHITE))
    MANA_CU = ((ColorSymbols.COLORLESS, MANA_GENERIC), (ColorSymbols.BLUE, MANA_BLUE))
    MANA_CB = ((ColorSymbols.COLORLESS, MANA_GENERIC), (ColorSymbols.BLACK, MANA_BLACK))
    MANA_CR = ((ColorSymbols.COLORLESS, MANA_GENERIC), (ColorSymbols.RED, MANA_RED))
    MANA_CG = ((ColorSymbols.COLORLESS, MANA_GENERIC), (ColorSymbols.GREEN, MANA_GREEN))
    MANA_2W = ((GenericSymbols.TWO, MANA_GENERIC), (ColorSymbols.WHITE, MANA_WHITE))
    MANA_2U = ((GenericSymbols.TWO, MANA_GENERIC), (ColorSymbols.BLUE, MANA_BLUE))
    MANA_2B = ((GenericSymbols.TWO, MANA_GENERIC), (ColorSymbols.BLACK, MANA_BLACK))
    MANA_2R = ((GenericSymbols.TWO, MANA_GENERIC), (ColorSymbols.RED, MANA_RED))
    MANA_2G = ((GenericSymbols.TWO, MANA_GENERIC), (ColorSymbols.GREEN, MANA_GREEN))

WIDTH = 8.5
HEIGHT = 11.0
DPI = 300.0
POINT_SIZE = (DPI / 72.0)

PIXEL_WIDTH = int(WIDTH * DPI)
PIXEL_HEIGHT = int(HEIGHT * DPI)

BIG_SIZES = [14, 12]
REGULAR_SIZES = [12, 9]
SMALL_SIZES = [9, 7]
ONLY_SMALL = [9]
ONLY_TINY = [7]

LONG_TEXT = 200

NARROW_LAYOUTS = [
    Layout.CLASS,
    Layout.ADVENTURE,
    Layout.PREPARE,
    Layout.SAGA,
]

DOUBLE_FRONT_LAYOUTS = [
    Layout.ADVENTURE,
    Layout.PREPARE,
]

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
            FontSet("Serif", "mplantin.ttf"),
            FontSet("Overprint", "Overprint TM.ttf"),
            FontSet("Blackletter", "PirataOne-Regular.ttf"),
            FontSet("Block", "Staatliches-Regular.ttf"),
            FontSet("Monospace", "CutiveMono-Regular.ttf"),
            FontSet("Typewriter", "Mom_typewrite.ttf"),
            FontSet("MTG", "Beleren2016-Bold.ttf"),
            FontSet("Console", "XanhMono-Regular.ttf")
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
            col.append(Row(
                Text(font.name).font_family(rf"fonts\{font.regular}").background_color("white").font_size(64).padding(15),
                Text(font.name).font_family(rf"fonts\{font.regular}").font_size(64).background_color("black").color("white").padding(15)
            ))

        col = Column(*col)

        canvas = Canvas()
        canvas.size(920, 115*len(self.fonts))
        canvas.background_color("white")
        img = canvas.render(col).to_pillow()
        img.save("font_preview.png", "PNG", resolution=100.0)

        return True


    def generate_symbol_page(self):
        col = Column(
            Column(
            #White and Blue
            Row(self.add_symbol_row(20, ColorSymbols.WHITE.value, MANA_WHITE),
            self.add_symbol_row(20, ColorSymbols.BLUE.value, MANA_BLUE)),
            #Black and Red
            Row(self.add_symbol_row(20, ColorSymbols.BLACK.value, MANA_BLACK),
            self.add_symbol_row(20, ColorSymbols.RED.value, MANA_RED)),
            #Red and Colorless
            Row(self.add_symbol_row(20, ColorSymbols.GREEN.value, MANA_GREEN),
                self.add_symbol_row(20, ColorSymbols.COLORLESS.value, MANA_GENERIC)),

            Row(Column(self.add_tap_rows(), self.add_generic_rows()),
                self.add_split_mana(5),
                self.add_special_rows(10))),

            #Big monochrome style
            Column(
                Row(
                    Column(
                #Black on White
                        Column(
                        self.add_symbol_row(10, ColorSymbols.WHITE.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.BLUE.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.BLACK.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.RED.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.GREEN.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.COLORLESS.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding=12),
                            self.add_symbol_row(10, TapSymbols.TAP.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding=12),
                            self.add_symbol_row(10, TapSymbols.OLD_TAP.value, background_color="white", symbol_color="black",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding=12),

                        ),

                    #White on black
                        Column(
                            self.add_symbol_row(10, ColorSymbols.WHITE.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.BLUE.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.BLACK.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.RED.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.GREEN.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding = 12),
                            self.add_symbol_row(10, ColorSymbols.COLORLESS.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding=12),
                            self.add_symbol_row(10, TapSymbols.TAP.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding=12),
                            self.add_symbol_row(10, TapSymbols.OLD_TAP.value, background_color="black", symbol_color="white",
                                                shadow=False, font_size=SYMBOL_SIZE * 2, padding=12)
                        ).background_color("black")
                    ),
                    Row(
                        self.add_generic_rows(5, "white", "black",
                                              False, SYMBOL_SIZE * 1.2, padding = 10),
                        self.add_generic_rows(5, "black", "white",
                                              False, SYMBOL_SIZE * 1.2, padding=10).background_color("black"),
                    ),
                    Column(
                        self.add_symbol_row(5, ColorSymbols.WHITE.value, MANA_WHITE, SYMBOL_COLOR, True,
                        SYMBOL_SIZE * 2.0, padding=8),
                        self.add_symbol_row(5, ColorSymbols.WHITE.value, MANA_WHITE, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8),
                        self.add_symbol_row(5, ColorSymbols.BLUE.value, MANA_BLUE, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.BLUE.value, MANA_BLUE, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.BLACK.value, MANA_BLACK, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.BLACK.value, MANA_BLACK, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.RED.value, MANA_RED, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.RED.value, MANA_RED, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.GREEN.value, MANA_GREEN, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.GREEN.value, MANA_GREEN, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.COLORLESS.value, MANA_GENERIC, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, ColorSymbols.COLORLESS.value, MANA_GENERIC, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, TapSymbols.TAP.value, MANA_GENERIC, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, TapSymbols.TAP.value, MANA_GENERIC, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, TapSymbols.OLD_TAP.value, MANA_GENERIC, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, TapSymbols.OLD_TAP.value, MANA_GENERIC, SYMBOL_COLOR, True,
                                            SYMBOL_SIZE * 2.0, padding=8, shadow_range=4),
                        self.add_symbol_row(5, TapSymbols.UNTAP.value, SYMBOL_COLOR, "white", False,
                                            SYMBOL_SIZE * 2.0, padding=8),
                        self.add_symbol_row(5, TapSymbols.UNTAP.value, SYMBOL_COLOR, "white", False,
                                            SYMBOL_SIZE * 2.0, padding=8),
                    )
                )
            )
        )

        canvas = Canvas()
        canvas.size(PIXEL_WIDTH, PIXEL_HEIGHT)
        canvas.background_color("white")
        canvas.padding(40)
        img = canvas.render(col).to_pillow().convert("RGB")
        img_path = rf"output\symbol_sheet.png"
        img.save(img_path, "PNG")

        pdf_path = rf"output\symbol_sheet.pdf"
        img_path = rf"output\symbol_sheet.png"

        layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))

        success = True
        try:
            Path(pdf_path).write_bytes(img2pdf.convert(img_path, layout_fun=layout))

        except PermissionError:
            success = False

        return success

    def add_generic_rows(self, count = 15, background_color = MANA_GENERIC, symbol_color = SYMBOL_COLOR, shadow = True,
                         font_size: float = SYMBOL_SIZE, padding = 4):
        col = []
        for symbol in GenericSymbols:
            col.append(self.add_symbol_row(count, symbol.value, background_color, symbol_color, shadow,
                                           font_size, padding))

        return Column(*col)

    def add_tap_rows(self):
        col = []
        for symbol in TapSymbols:
            if symbol == TapSymbols.UNTAP:
                col.append(self.add_symbol_row(15, symbol.value, SYMBOL_COLOR, symbol_color="white"))

            else:
                col.append(self.add_symbol_row(15, symbol.value, MANA_GENERIC))

        return Column(*col)

    def add_symbol_row(self, count: int, symbol, background_color, symbol_color = SYMBOL_COLOR, shadow = True,
                       font_size : float = SYMBOL_SIZE, padding = 4, shadow_range = 2):
        row = []

        for i in range(count):
            text = (Text(symbol).font_family(SYMBOL_FONT).color(symbol_color).background_color(background_color).font_size(font_size)
                    .border_radius(100).padding(padding).margin(ICON_MARGIN))

            if shadow:
                text.box_shadows(Shadow((-shadow_range,shadow_range), 0, symbol_color))
            row.append(text)

        return Row(*row)

    def add_split_mana(self, count):
        col = []

        for pair in SplitSymbols:
            row = []
            for i in range(count):
                row.append(Row(
                    #Gradient
                    Text("  ").font_family(SYMBOL_FONT).background_color(LinearGradient([pair.value[0][1], pair.value[1][1]], stops=(0.5, 0.5),
                    start_point=(0,0), end_point=(1,1))).padding(10).border_radius(100).font_size((SYMBOL_SIZE/2)+1).margin(ICON_MARGIN)
                           .box_shadows(Shadow((-2,2), 0, SYMBOL_COLOR)),

                    #Left Symbol
                    Text(str(pair.value[0][0].value)).font_family(SYMBOL_FONT)
                        .absolute_position(top=SPLIT_SYMBOL_OFFSET, left=SPLIT_SYMBOL_OFFSET).font_size(SYMBOL_SIZE/1.9)
                        .color(SYMBOL_COLOR),

                    #Right Symbol
                    Text(str(pair.value[1][0].value)).font_family(SYMBOL_FONT)
                        .absolute_position(right=SPLIT_SYMBOL_OFFSET, bottom=SPLIT_SYMBOL_OFFSET).font_size(SYMBOL_SIZE/1.9)
                        .color(SYMBOL_COLOR)
                ))

            col.append(Row(*row))

        return Column(*col)

    def add_special_rows(self, count):
        col = []
        #loyalty can start from 0-7
        for x in range(8):
            row = []
            for y in range(count):
                row.append(self.add_loyalty(str(x)))
            col.append(Row(*row))

        col.append(self.add_special_symbol_row(count, SpecialSymbols.MDFC_FRONT.value))
        col.append(self.add_special_symbol_row(count, SpecialSymbols.MDFC_BACK.value))

        return Column(*col)

    def add_special_symbol_row(self, count: int, symbol):
        row = []
        for i in range(count):
            row.append(Text(symbol).font_family(SYMBOL_FONT).color(SYMBOL_COLOR).font_size(SYMBOL_SIZE*2)
            .padding(2).margin(ICON_MARGIN))

        return Row(*row)

    def add_loyalty(self, value):
        dist = 4
        return Column(Text(SpecialSymbols.LOYALTY.value).font_family(SYMBOL_FONT)
               .font_size(SYMBOL_SIZE * 4).color(SYMBOL_COLOR).margin(ICON_MARGIN).
                      text_shadows(
                Shadow((dist, 0), 0, "#ddd"),Shadow((0, dist), 0, "#aaa"),
                    Shadow((-dist, 0), 0, "#aaa"), Shadow((0, -dist), 0, "#ddd")),
               Text(value).font_family(TEXT_FONT).absolute_position(top=40, left=50).font_size(SYMBOL_SIZE*1.8).color("white")
                      .text_align(TextAlign.CENTER))

    def generate_card_page(self, face: Faces = Faces.Front) -> str:
        fonts = [
            self.get_font_for_name(self.custom_data["style1"]),
            self.get_font_for_name(self.custom_data["style2"]),
            self.get_font_for_name(self.custom_data["style3"]),
        ]

        # Col Main Page
        col = []

        # Name
        name_sizes = BIG_SIZES
        if face == Faces.Back and self.card.layout in DOUBLE_FRONT_LAYOUTS:
            name_sizes = SMALL_SIZES

        if self.custom_data["nickname"] == "":
            print("[LayoutGenerator][generate_card] Adding name")
            col.append(self.generate_data_row(self.format_name(Scryfall.get_card_name(self.card, face)), fonts, name_sizes,
                                              FontWeight.Bold))
        else:
            print("[LayoutGenerator][generate_card] Adding name with nickname")
            col.append(self.generate_data_row(self.format_name(self.custom_data["nickname"]), fonts, name_sizes,
                                              FontWeight.Bold))
            col.append(self.generate_data_row(self.format_name(Scryfall.get_card_name(self.card, face)), fonts, SMALL_SIZES,
                                              FontWeight.Italic))

        # Type
        print("[LayoutGenerator][generate_card] Adding type")
        type_sizes = REGULAR_SIZES
        if face == Faces.Back and self.card.layout in DOUBLE_FRONT_LAYOUTS:
            type_sizes = SMALL_SIZES
        col.append(
            self.generate_data_row(self.format_type_line(Scryfall.get_type_line(self.card, face)), fonts, type_sizes,
                                   FontWeight.Regular))

        # Oracle
        print("[LayoutGenerator][generate_card] Adding oracle")
        oracle_sizes = REGULAR_SIZES
        if len(Scryfall.get_card_oracle(self.card, face)) > LONG_TEXT:
            oracle_sizes = ONLY_TINY
        if self.card.type_line == "Dungeon":
            col.append(self.generate_data_row(
                self.format_oracle(Scryfall.get_card_oracle(self.card, face)),
                # Wrap text and remove any reminder text
                fonts, ONLY_SMALL, FontWeight.Regular, True))
        if self.card.layout in NARROW_LAYOUTS:
            col.append(self.generate_data_row(
                self.format_oracle(Scryfall.get_card_oracle(self.card, face)),
                # Wrap text and remove any reminder text
                fonts, SMALL_SIZES, FontWeight.Regular, True))
        else:
            col.append(self.generate_data_row(
                self.format_oracle(Scryfall.get_card_oracle(self.card, face)),
                # Wrap text and remove any reminder text
                fonts, oracle_sizes, FontWeight.Regular))

        row = []

        # Mana Value
        mana_sizes = REGULAR_SIZES
        if face == Faces.Back and self.card.layout in DOUBLE_FRONT_LAYOUTS:
            mana_sizes = SMALL_SIZES
        if Scryfall.get_mana_value(self.card, face):
            print("[LayoutGenerator][generate_card] Adding mana value")
            row.append(
                self.generate_data_row(self.format_mana(Scryfall.get_mana_value(self.card, face)), fonts, mana_sizes,
                                       FontWeight.Regular))

        # Power/Toughness
        if Scryfall.get_power(self.card, face) and Scryfall.get_toughness(self.card, face):
            print("[LayoutGenerator][generate_card] Adding P/T")
            power = Scryfall.get_power(self.card, face)
            if not self.custom_data["power"] == "":
                power = self.custom_data["power"]

            toughness = Scryfall.get_toughness(self.card, face)
            if not self.custom_data["toughness"] == "":
                toughness = self.custom_data["toughness"]

            row.append(self.generate_data_row(f"{power}/{toughness}", fonts, REGULAR_SIZES, FontWeight.Regular))

        #Loyalty
        if Scryfall.get_loyalty(self.card, face):
            print("[LayoutGenerator][generate_card] Adding loyalty")
            row.append(self.generate_data_row(Scryfall.get_loyalty(self.card, face), fonts, REGULAR_SIZES, FontWeight.Regular))

        col = Column(
            *col,
            Row(*row)
        )
        col.padding(0.15 * DPI)

        canvas = Canvas()
        canvas.size(PIXEL_WIDTH, PIXEL_HEIGHT)
        canvas.background_color("white")
        img = canvas.render(col).to_pillow().convert("RGB")
        img_path = rf"output\{Scryfall.get_card_name(self.card)}-{face.name}.png"
        img.save(img_path, "PNG")
        return img_path

    def generate_card(self) -> bool:
        print("[LayoutGenerator][generate_card] Generating card...")

        images = []

        if self.card.card_faces:
            images.append(self.generate_card_page(Faces.Front))
            images.append(self.generate_card_page(Faces.Back))
        else:
            images.append(self.generate_card_page(Faces.Front))

        pdf_path = rf"output\{Scryfall.get_card_name(self.card)}.pdf"

        try:
            layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))
            Path(pdf_path).write_bytes(img2pdf.convert(images, layout_fun=layout))
            os.startfile(rf"{pdf_path}")
            return True
        except PermissionError:
            print(f"[LayoutGenerator][generate_card] Permission error!")
            return False

    def generate_data_row(self, text, fonts, sizes, weight, set_as_row = False):
        row = []
        print(f"Generating row data for {text}")
        for font in fonts:
            print(f"At font {font.name}")
            row.append(self.generate_data_column(text, font, sizes, weight, set_as_row))

        return Row(*row)

    def generate_data_column(self, text, font, sizes, weight, set_as_row):
        column = []
        print (f"Generating column data for font {font.name}")
        for size in sizes:
            print(f"At size {size}")
            column.append(self.generate_data_set(text, font, size, weight, set_as_row))

        return Column(*column)

    def generate_data_set(self, text, font : FontSet, size, weight : FontWeight, set_as_row):
        print(f"Generating data for font {font.name}")
        if size >= 14:
            text = self.wrap_text(18, text)
        font = self.get_weight_for_font(font, weight)
        regular = Text(text)
        self.style_text(regular, font, size)

        invert = Text(text)
        self.style_text(invert, font, size, True)

        if set_as_row:
            return Row(regular, invert)
        else:
            return Column(regular, invert)

    def get_weight_for_font(self, font : FontSet, weight):
        if weight == FontWeight.Bold:
            return font.bold
        if weight == FontWeight.Italic:
            return font.italic

        return font.regular

    def style_text(self, text: Text, font, size, invert=False):
        text.font_family(rf"fonts\{font}").font_size(size*POINT_SIZE).margin(0.05*DPI).padding(0.05 * DPI)
        if invert:
            text.background_color("black")
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
        if len(text) > 30:
            text = text.replace(" \u2014 ", "\n")
        return text

    def format_mana(self, text: str):
        return text.replace("{", "").replace("}", "")

    def format_oracle(self, text: str):
        text = self.remove_parenthenticals(text)
        text = text.replace("{", "").replace("}", "")

        if self.card.type_line == "Dungeon":
            print("Formatting dungeon")
            text = text.replace(" \u2014", ":")
            text = self.wrap_text(18, text)
        elif self.card.layout in NARROW_LAYOUTS:
            text = self.wrap_text(18, text)
        else:
            if len(text) > LONG_TEXT:
                text = self.wrap_text(48, text)
            else:
                text = self.wrap_text(32, text)
        return text

    def remove_parenthenticals(self, text: str):
        return re.sub("[\\(\\[].*?[\\)\\]]", "", text)