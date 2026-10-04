import tkinter
import os
from tkinter import ttk
from tkinter.ttk import Combobox

from PIL import Image, ImageTk
from io import BytesIO
from layout_generator import Casing
from scryfall.card import Card
import sv_ttk

IMAGE_SCALE = 0.4
FONT_PREVIEW_PATH = "font_preview.png"

class BuilderApp:
    search_callback = None #event we invoke when search is called.
    generate_callback = None
    font_preview_callback = None
    symbol_sheet_callback = None

    def search(self, event):
        print(f"[BuilderApp][search] Search button pressed! Searching '{self.search_entry.get()}'")
        if self.search_callback:
            self.search_callback(self.search_entry.get())

    def create_font_preview(self, event):
        print(f"[BuilderApp][search] Font Preview button pressed!")
        if self.font_preview_callback:
            self.font_preview_callback()

    def generate_symbol_sheet(self, event):
        print(f"[BuilderApp][search] Generate symbol sheet pressed!")
        if self.symbol_sheet_callback:
            self.symbol_sheet_callback()

    def add_card(self, event):
        print(f"[BuilderApp][add_card]")
        if self.searched_card is None:
            print(f"[BuilderApp][add_card] searched card was none!")
            return

        print(f"[BuilderApp][add_card] adding searched card {self.searched_card.name}")
        self.cards.append({
            "card": self.searched_card,
            "custom_data": self.get_custom_data()
        })

        self.update_card_list()

    def get_custom_data(self):
        print(f"[BuilderApp][get_custom_data]")
        return {
                "nickname": self.custom_name_entry.get(),
                "power": self.power_entry.get(),
                "toughness": self.toughness_entry.get(),
                "style": self.style.get()
            }

    def generate(self, event):
        print(f"[BuilderApp][search] Generate button pressed!")

        if self.generate_callback:
            self.generate_callback(self.cards)

    def clear_cards(self, event):
        print(f"[BuilderApp][clear_cards]")

        self.cards = []
        self.update_card_list()

    def update_search_result(self, image, card):
        print(f"[BuilderApp][update_search_result] Search result updated")

        if not image:
            return

        img = Image.open(BytesIO(image))
        img = img.resize((int(img.size[0] * IMAGE_SCALE), int(img.size[1] * IMAGE_SCALE)), resample=Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.card_image = ttk.Label(self.card_image_frame, image=img)
        self.card_image.image = img
        self.card_image.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.N)

        self.searched_card = card

    def get_card_list_card_label(self, card):
        label = f"{card["card"].name}"

        if card["custom_data"]["nickname"] != "":
            label += f" \"{card["custom_data"]["nickname"]}\""

        if card["custom_data"]["power"] != "" and card["custom_data"]["toughness"] != "":
            label += f" {card["custom_data"]["power"]}/{card["custom_data"]["toughness"]}"

        label += f", {card["custom_data"]["style"]}\n"
        return label


    def update_card_list(self):
        print("[BuilderApp][update_card_list] Update card list")

        self.card_list = ""
        for card in self.cards:
            self.card_list += self.get_card_list_card_label(card)

        print(f"[BuilderApp][update_card_list] Update card list {self.card_list}")
        self.card_list_label.configure(text=self.card_list)

    def update_font_preview(self):
        if not os.path.isfile(FONT_PREVIEW_PATH):
            print("Failed to find preview image!")
            return

        img = Image.open(FONT_PREVIEW_PATH)
        img = img.resize((int(img.size[0] * IMAGE_SCALE), int(img.size[1] * IMAGE_SCALE)),
                         resample=Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.font_preview_image = ttk.Label(self.font_preview, image=img)
        self.font_preview_image.image = img
        self.font_preview_image.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.N)

    def __init__(self, styles):
        self.cards = []
        self.searched_card: Card | None = None
        self.styles = styles
        self.style : Combobox | None = None
        self.font_preview_image: ttk.Label | None = None
        self.style_frame = None

        self.root = tkinter.Tk()

        self.root.title("Proxy Collage Printer")

        ##Search Frame
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.NSEW)
        #Search entry area
        self.search_frame = ttk.LabelFrame(self.left_frame, text="Search")
        self.search_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.EW)

        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)
        self.search_entry.bind("<Return>", self.search)

        self.search_button = ttk.Button(self.search_frame, text="Search")
        self.search_button.grid(column=1, row=0, padx=5, pady=5, sticky=tkinter.EW)
        self.search_button.bind("<Button-1>", self.search)
        #
        ##

        ##Card 1

        #Card Preview
        self.card_image_frame = ttk.LabelFrame(self.left_frame, text="Card Preview")
        self.card_image_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.card_image = None
        #
        ##

        ##Actions and Data frame
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.grid(column=1, row=0, padx=5, pady=5, sticky=tkinter.NSEW)
        #Actions Frame
        self.actions_frame = ttk.LabelFrame(self.right_frame, text="Actions")
        self.actions_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.generate_button = ttk.Button(self.actions_frame, text="Refresh Font Preview")
        self.generate_button.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.EW)
        self.generate_button.bind("<Button-1>", self.create_font_preview)

        self.generate_button = ttk.Button(self.actions_frame, text="Generate Symbol Sheet")
        self.generate_button.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.EW)
        self.generate_button.bind("<Button-1>", self.generate_symbol_sheet)
        #

        # Custom Data
        self.data_frame = ttk.LabelFrame(self.right_frame, text="Custom Data")
        self.data_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.nickname_frame = ttk.LabelFrame(self.data_frame, text="Nickname")
        self.nickname_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.custom_name_entry = ttk.Entry(self.nickname_frame)
        self.custom_name_entry.grid(column=1, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.pt_group = ttk.LabelFrame(self.data_frame, text="Power/Toughness", padding=5)
        self.pt_group.grid(column=0, row=2, padx=5, pady=5, sticky=tkinter.NSEW)

        self.power_entry = ttk.Entry(self.pt_group, width=5)
        self.power_entry.grid(column=0, row=0, padx=2, pady=2, sticky=tkinter.EW)
        ttk.Label(self.pt_group, text="/").grid(column=1, row=0, padx=5, pady=5)
        self.toughness_entry = ttk.Entry(self.pt_group, width=5)
        self.toughness_entry.grid(column=2, row=0, padx=2, pady=2, sticky=tkinter.EW)

        self.add_style_dropdowns(self.data_frame, 0)
        #
        ##

        ##Cards Frame
        self.cards_frame = ttk.LabelFrame(self.root, text="Cards")
        self.cards_frame.grid(column=2, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.add_card_button = ttk.Button(self.cards_frame, text="Add Card", width=20)
        self.add_card_button.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.EW)
        self.add_card_button.bind("<Button-1>", self.add_card)
        self.card_list_label = ttk.Label(self.cards_frame, text="")
        self.card_list_label.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.generate_button = ttk.Button(self.cards_frame, text="Generate")
        self.generate_button.grid(column=0, row=2, padx=5, pady=5, sticky=tkinter.EW)
        self.generate_button.bind("<Button-1>", self.generate)

        self.generate_button = ttk.Button(self.cards_frame, text="Clear")
        self.generate_button.grid(column=0, row=3, padx=5, pady=5, sticky=tkinter.EW)
        self.generate_button.bind("<Button-1>", self.clear_cards)
        ##

        ##Font Preview Frame
        self.font_preview = ttk.LabelFrame(self.root, text="Font Preview")
        self.font_preview.grid(column=3, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.update_font_preview()

        self.status = ttk.Label(self.root, text="Status: Ready", foreground="white")
        self.status.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.EW)
        ##

    def add_style_dropdowns(self, parent, row):
        self.style_frame = ttk.LabelFrame(parent, text="Styles")
        self.style_frame.grid(column=0, row= row, padx=5, pady=5, sticky=tkinter.NSEW)

        self.style = self.add_style_dropdown(0, 0, self.style_frame)

    def add_style_dropdown(self, start_index, row, parent):
        style = ttk.Combobox(parent, values=[style.name for style in self.styles])
        style["state"] = "readonly"
        style.current(start_index)
        style.grid(column=0, row=row, padx=5, pady=5, sticky=tkinter.EW)
        return style

    def add_casing_dropdown(self, row, parent):
        style = ttk.Combobox(parent, values=[case.value for case in Casing])
        style["state"] = "readonly"
        style.current(0)
        style.grid(column=1, row=row, padx=5, pady=5, sticky=tkinter.EW)
        return style

    def push_status(self, label, color = "white"):
        self.status["text"] = f"Status: {label}"
        self.status["foreground"] = color
        self.status.update()

    def run(self):
        sv_ttk.set_theme("dark")
        self.root.mainloop()