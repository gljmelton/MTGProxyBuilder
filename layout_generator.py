import os
import re
import textwrap

import img2pdf
from enum import Enum
from pathlib import Path
from pictex import Canvas, Row, Column, Text, Shadow, TextAlign, LinearGradient
from scryfall.scryfall import Scryfall, Faces, Layout
from itertools import zip_longest

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
CARD_WIDTH = 2.25
DPI = 300.0
POINT_SIZE = (DPI / 72.0)

PIXEL_WIDTH = int(WIDTH * DPI)
PIXEL_HEIGHT = int(HEIGHT * DPI)

BIG_SIZES = [14, 12]
REGULAR_SIZES = [10, 8]
SMALL_SIZES = [9, 7]
ONLY_SMALL = [9]
ONLY_TINY = [7]

LONG_TEXT = 250
EXTRA_LONG_TEXT = 350

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

class FontSet:
    def __init__(self, name, regular, bold = None, italic = None, size_multiplier : float = 1.0):
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

        self.size_multiplier = size_multiplier

class LayoutGenerator:
    def __init__(self):
        self.cards = None

        self.fonts = [
            FontSet("SansSerif", "BeVietnamPro-Black.ttf", size_multiplier=0.8),
            FontSet("Serif", "AdvercaseFont-Bold.ttf"),
            FontSet("Overprint", "Overprint TM.ttf"),
            FontSet("Blackletter", "PirataOne-Regular.ttf"),
            FontSet("Block", "Staatliches-Regular.ttf"),
            FontSet("Monospace", "CutiveMono-Regular.ttf"),
            FontSet("Typewriter", "Mom_typewrite.ttf", size_multiplier= 0.75),
            FontSet("MTG", "Beleren2016-Bold.ttf"),
            FontSet("Console", "XanhMono-Regular.ttf"),
            FontSet("Cyber", "Cyber Brush.otf", size_multiplier= 0.75),
            FontSet("Rock Metal", "BigFishDD-Regular.otf", size_multiplier= 1.25),
        ]

    def get_fonts(self):
        return self.fonts

    def get_font_from_name(self, name):
        for font in self.fonts:
            if font.name == name:
                return font.regular

        return None

    def get_font_scale_from_name(self, name):
        for font in self.fonts:
            if font.name == name:
                return font.size_multiplier

        return 1

    def generate(self, cards: list) -> bool:
        if cards is None or len(cards) == 0:
            print("[LayoutGenerator][generate] Attempting to generate card with no card!")
            return False

        print("[LayoutGenerator][generate] Generating layout...")
        self.cards = cards

        return self.generate_cards()

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

    @staticmethod
    def add_symbol_row(count: int, symbol, background_color, symbol_color = SYMBOL_COLOR, shadow = True,
                       font_size : float = SYMBOL_SIZE, padding = 4, shadow_range = 2):
        row = []

        for i in range(count):
            text = (Text(symbol).font_family(SYMBOL_FONT).color(symbol_color).background_color(background_color).font_size(font_size)
                    .border_radius(100).padding(padding).margin(ICON_MARGIN))

            if shadow:
                text.box_shadows(Shadow((-shadow_range,shadow_range), 0, symbol_color))
            row.append(text)

        return Row(*row)

    @staticmethod
    def add_split_mana(count):
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

    @staticmethod
    def add_special_symbol_row(count: int, symbol):
        row = []
        for i in range(count):
            row.append(Text(symbol).font_family(SYMBOL_FONT).color(SYMBOL_COLOR).font_size(SYMBOL_SIZE*2)
            .padding(2).margin(ICON_MARGIN))

        return Row(*row)

    @staticmethod
    def add_loyalty(value):
        dist = 4
        return Column(Text(SpecialSymbols.LOYALTY.value).font_family(SYMBOL_FONT)
               .font_size(SYMBOL_SIZE * 4).color(SYMBOL_COLOR).margin(ICON_MARGIN).
                      text_shadows(
                Shadow((dist, 0), 0, "#ddd"),Shadow((0, dist), 0, "#aaa"),
                    Shadow((-dist, 0), 0, "#aaa"), Shadow((0, -dist), 0, "#ddd")),
               Text(value).font_family(TEXT_FONT).absolute_position(top=40, left=50).font_size(SYMBOL_SIZE*1.8).color("white")
                      .text_align(TextAlign.CENTER))

    def generate_card_column(self, card, face: Faces = Faces.Front) -> Column:
        # Col Main Page
        col = []

        # Name
        name_sizes = BIG_SIZES
        if face == Faces.Back and card["card"].layout in DOUBLE_FRONT_LAYOUTS:
            name_sizes = SMALL_SIZES

        if card["custom_data"]["nickname"] == "":
            print("[LayoutGenerator][generate_card] Adding name")
            col.append(self.generate_data_row(self.format_name(Scryfall.get_card_name(card["card"], face)),
                                              card["custom_data"]["style"], name_sizes))
        else:
            print("[LayoutGenerator][generate_card] Adding name with nickname")
            col.append(self.generate_data_row(self.format_name(card["custom_data"]["nickname"]),
                                              card["custom_data"]["style"], name_sizes))
            col.append(self.generate_data_row(self.format_name(Scryfall.get_card_name(card["card"], face)),
                                              card["custom_data"]["style"], SMALL_SIZES))

        # Type
        print("[LayoutGenerator][generate_card] Adding type")
        type_sizes = REGULAR_SIZES
        if face == Faces.Back and card["card"].layout in DOUBLE_FRONT_LAYOUTS:
            type_sizes = SMALL_SIZES
        col.append(
            self.generate_data_row(self.format_type_line(Scryfall.get_type_line(card["card"], face)),
                                   card["custom_data"]["style"], type_sizes))

        # Oracle
        print("[LayoutGenerator][generate_card] Adding oracle")
        oracle_sizes = REGULAR_SIZES
        width_override = 1
        as_row = False
        if len(Scryfall.get_card_oracle(card["card"], face)) > LONG_TEXT:
            oracle_sizes = SMALL_SIZES
        if len(Scryfall.get_card_oracle(card["card"], face)) > EXTRA_LONG_TEXT:
            oracle_sizes = ONLY_TINY
        if Scryfall.get_type_line(card["card"]) == "Dungeon":
            print("[LayoutGenerator][generate_card_column] Adding oracle for dungeon")
            oracle_sizes = ONLY_SMALL
            width_override = 0.3
            as_row = True
        if card["card"].layout in NARROW_LAYOUTS:
            print("[LayoutGenerator][generate_card_column] Adding oracle for narrow card")
            oracle_sizes = SMALL_SIZES
            width_override = 0.3
            as_row = True

        col.append(self.generate_data_row(
            self.format_oracle(Scryfall.get_card_oracle(card["card"], face),
                               Scryfall.get_type_line(card["card"], face)),
            # Wrap text and remove any reminder text
            card["custom_data"]["style"], oracle_sizes, as_row, width_override))

        row = []

        # Mana Value
        mana_sizes = REGULAR_SIZES
        if face == Faces.Back and card["card"].layout in DOUBLE_FRONT_LAYOUTS:
            mana_sizes = SMALL_SIZES
        if Scryfall.get_mana_value(card["card"], face):
            print("[LayoutGenerator][generate_card] Adding mana value")
            row.append(
                self.generate_data_row(self.format_mana(Scryfall.get_mana_value(card["card"], face)),
                    card["custom_data"]["style"], mana_sizes))

        # Power/Toughness
        if Scryfall.get_power(card["card"], face) and Scryfall.get_toughness(card["card"], face):
            print("[LayoutGenerator][generate_card] Adding P/T")
            power = Scryfall.get_power(card["card"], face)
            if not card["custom_data"]["power"] == "":
                power = card["custom_data"]["power"]

            toughness = Scryfall.get_toughness(card["card"], face)
            if not card["custom_data"]["toughness"] == "":
                toughness = card["custom_data"]["toughness"]

            row.append(self.generate_data_row(f"{power}/{toughness}",
                                              card["custom_data"]["style"], REGULAR_SIZES))

        #Loyalty
        if Scryfall.get_loyalty(card["card"], face):
            print("[LayoutGenerator][generate_card] Adding loyalty")
            row.append(self.generate_data_row(Scryfall.get_loyalty(card["card"], face),
                                              card["custom_data"]["style"], REGULAR_SIZES))

        col = Column(
            *col,
            Row(*row)
        )
        col.padding(0.15 * DPI)

        return col

    def grouper(self, iterable, n, *, incomplete='fill', fillvalue=None):
        "Collect data into non-overlapping fixed-length chunks or blocks."
        # grouper('ABCDEFG', 3, fillvalue='x')       → ABC DEF Gxx
        # grouper('ABCDEFG', 3, incomplete='strict') → ABC DEF ValueError
        # grouper('ABCDEFG', 3, incomplete='ignore') → ABC DEF
        iterators = [iter(iterable)] * n
        match incomplete:
            case 'fill':
                return zip_longest(*iterators, fillvalue=fillvalue)
            case 'strict':
                return zip(*iterators, strict=True)
            case 'ignore':
                return zip(*iterators)
            case _:
                raise ValueError('Expected fill, strict, or ignore')

    def generate_cards(self) -> bool:
        print("[LayoutGenerator][generate_card] Generating card...")

        images = []

        columns = []

        for card in self.cards:
            if card["card"].card_faces:
                columns.append(self.generate_card_column(card, Faces.Front))
                columns.append(self.generate_card_column(card, Faces.Back))
            else:
                columns.append(self.generate_card_column(card, Faces.Front))

        page_groups = self.grouper(columns, 3, incomplete='fill', fillvalue=None)

        page = 0
        for group in page_groups:
            cols_for_page = []
            for card in group:
                if card is not None:
                    cols_for_page.append(card)

            canvas = Canvas()
            canvas.size(PIXEL_WIDTH, PIXEL_HEIGHT)
            canvas.background_color("white")
            img = canvas.render(Row(*cols_for_page)).to_pillow().convert("RGB").crop((0, 0, PIXEL_WIDTH, PIXEL_HEIGHT))
            img_path = rf"output\{Scryfall.get_card_name(self.cards[0]["card"])}-{page}.png"
            img.save(img_path, "PNG")
            page += 1
            images.append(img_path)

        pdf_path = rf"output\{Scryfall.get_card_name(self.cards[0]["card"])}.pdf"

        try:
            layout = img2pdf.get_fixed_dpi_layout_fun((DPI, DPI))
            Path(pdf_path).write_bytes(img2pdf.convert(images, layout_fun=layout))
            
            os.startfile(rf"{pdf_path}")
            return True
        except PermissionError:
            print(f"[LayoutGenerator][generate_card] Permission error!")
            return False

    def generate_data_row(self, text, font, sizes, set_as_row = False, width_override = 1):
        row = []
        print("[layout_generator][generate_data_row]")
        print(f"At font {font}")
        row.append(self.generate_data_column(text, font, sizes, set_as_row, width_override))

        return Row(*row)

    def generate_data_column(self, text, font, sizes, set_as_row, width_override):
        column = []
        print (f"Generating column data for font {font}")
        for size in sizes:
            print(f"At size {size}")
            column.append(self.generate_data_set(text, font, size, set_as_row, width_override))

        return Column(*column)

    def generate_data_set(self, text, font : str, size, set_as_row, width_override):
        print(f"Generating data for font {font}")
        regular = Text(text)
        self.style_text(regular, font, size)

        invert = Text(text)
        self.style_text(invert, font, size, True)

        if set_as_row:
            return Row(regular, invert).max_width(CARD_WIDTH * DPI * width_override)
        else:
            return Column(regular, invert).max_width(CARD_WIDTH * DPI * width_override)

    def style_text(self, text: Text, font, size, invert=False):
        (text.font_family(rf"fonts\{self.get_font_from_name(font)}")
         .font_size(size*POINT_SIZE*self.get_font_scale_from_name(font))
         .margin(0.05*DPI)
         .padding(0.05 * DPI)
         .max_width(CARD_WIDTH * DPI))

        if invert:
            (text
             .background_color("black")
             .color("white"))

        else:
            (text
             .background_color("white")
             .color("black"))

    @staticmethod
    def wrap_text(width: int, text: str):
        return '\n\n'.join(['\n'.join(textwrap.wrap(line, width,
                 break_long_words=False, replace_whitespace=False))
                 for line in text.splitlines() if line.strip() != ''])

    @staticmethod
    def format_name(text: str):
        return text

    @staticmethod
    def format_type_line(text: str):
        return text

    @staticmethod
    def format_mana(text: str):
        return text.replace("{", "").replace("}", "")

    def format_oracle(self, text: str, type: str):
        text = self.remove_parenthenticals(text)
        text = text.replace("{", "").replace("}", "").replace("\n", "\n\n")

        if type == "Dungeon":
            print("Formatting dungeon")
            text = text.replace(" \u2014", ":").replace("\n", "\n\n")
        return text

    @staticmethod
    def remove_parenthenticals(text: str):
        return re.sub("[\\(\\[].*?[\\)\\]]", "", text)