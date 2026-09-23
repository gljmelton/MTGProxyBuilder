import tkinter
from tkinter import ttk
from tkinter.ttk import Combobox

from PIL import Image, ImageTk
from io import BytesIO
import sv_ttk
from fontTools.merge import options

IMAGE_SCALE = 0.4

class BuilderApp:

    search_callback = None #Event we invoke when search is called.
    generate_callback = None

    def search(self, event):
        print(f"[BuilderApp][search] Search button pressed! Searching '{self.search_entry.get()}'")
        if self.search_callback:
            self.search_callback(self.search_entry.get())

    def generate(self, event):
        print(f"[BuilderApp][search] Generate button pressed!")

        if self.generate_callback:
            self.generate_callback({
                "nickname": self.custom_name_entry.get(),
                "power": self.power_entry.get(),
                "toughness": self.toughness_entry.get(),
                "style1": self.style1.get(),
                "style2": self.style2.get(),
                "style3": self.style3.get()
            })

    def update_search_result(self, value):
        print(f"[BuilderApp][update_search_result] Search result updated")

        if not value:
            pass

        img = Image.open(BytesIO(value))
        img = img.resize((int(img.size[0] * IMAGE_SCALE), int(img.size[1] * IMAGE_SCALE)), resample=Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        self.card_image = ttk.Label(self.card_image_frame, image=img)
        self.card_image.image = img
        self.card_image.grid(column=0, row=0, padx=5, pady=5)

    def __init__(self, styles):
        self.styles = styles
        self.style1 : Combobox | None = None
        self.style2 : Combobox | None = None
        self.style3 : Combobox | None = None
        self.style1_preview : tkinter.Label | None = None
        self.style2_preview : tkinter.Label | None = None
        self.style3_preview : tkinter.Label | None = None
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

        #Card Preview
        self.card_image_frame = ttk.LabelFrame(self.left_frame, text="Card Preview")
        self.card_image_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.card_image = None
        #
        ##

        ##Right fram
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.grid(column=1, row=0, padx=5, pady=5, sticky=tkinter.NSEW)
        #Actions Frame
        self.actions_frame = ttk.LabelFrame(self.right_frame, text="Actions")
        self.actions_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.generate_button = ttk.Button(self.actions_frame, text="Generate")
        self.generate_button.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.EW)
        self.generate_button.bind("<Button-1>", self.generate)
        #

        # Custom Data
        self.data_frame = ttk.LabelFrame(self.right_frame, text="Custom Data")
        self.data_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.nickname_frame = ttk.LabelFrame(self.data_frame, text="Nickname")
        self.nickname_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.custom_name_entry = ttk.Entry(self.nickname_frame)
        self.custom_name_entry.grid(column=1, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.pt_group = ttk.LabelFrame(self.data_frame, text="Power/Toughness", padding=5)
        self.pt_group.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.power_entry = ttk.Entry(self.pt_group, width=5)
        self.power_entry.grid(column=0, row=0, padx=2, pady=2, sticky=tkinter.EW)
        ttk.Label(self.pt_group, text="/").grid(column=1, row=0, padx=5, pady=5)
        self.toughness_entry = ttk.Entry(self.pt_group, width=5)
        self.toughness_entry.grid(column=2, row=0, padx=2, pady=2, sticky=tkinter.EW)

        self.add_style_dropdowns(self.data_frame, 2)
        #
        ##

        self.status = ttk.Label(self.root, text="Status: Ready", foreground="white")
        self.status.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.EW)

    def add_style_dropdowns(self, parent, row):
        self.style_frame = ttk.LabelFrame(parent, text="Styles")
        self.style_frame.grid(column=0, row= row, padx=5, pady=5, sticky=tkinter.NSEW)

        self.style1 = self.add_style_dropdown(0, 0, self.style_frame)
        self.style2 = self.add_style_dropdown(1, 1, self.style_frame)
        self.style3 = self.add_style_dropdown(2, 2, self.style_frame)

    def add_style_dropdown(self, start_index, row, parent):
        style = ttk.Combobox(parent, values=[style.name for style in self.styles])
        style["state"] = "readonly"
        style.current(start_index)
        style.grid(column=0, row=row, padx=5, pady=5, sticky=tkinter.EW)
        return style

    def push_status(self, label, color = "white"):
        self.status["text"] = f"Status: {label}"
        self.status["foreground"] = color
        self.status.update()

    def run(self):
        sv_ttk.set_theme("dark")
        self.root.mainloop()