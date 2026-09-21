import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import sv_ttk

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
                "toughness": self.toughness_entry.get()
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

    def __init__(self):
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

        ##Actions Frame
        self.actions_frame = ttk.LabelFrame(self.root, text="Actions")
        self.actions_frame.grid(column=1, row=0, padx=10, pady=10, sticky=tkinter.NSEW)

        # Custom Name
        self.alias_frame = ttk.LabelFrame(self.actions_frame, text="Custom Data")
        self.alias_frame.grid(column=0, row=0, padx=5, pady=5)

        self.nickname_frame = ttk.LabelFrame(self.alias_frame, text="Nickname")
        self.nickname_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.custom_name_entry = ttk.Entry(self.nickname_frame)
        self.custom_name_entry.grid(column=1, row=0, padx=5, pady=5, sticky=tkinter.NSEW)

        self.pt_group = ttk.LabelFrame(self.alias_frame, text="Power/Toughness", padding=5)
        self.pt_group.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        self.power_entry = ttk.Entry(self.pt_group, width=5)
        self.power_entry.grid(column=0, row=0, padx=2, pady=2)
        ttk.Label(self.pt_group, text="/").grid(column=1, row=0, padx=5, pady=5)
        self.toughness_entry = ttk.Entry(self.pt_group, width=5)
        self.toughness_entry.grid(column=2, row=0, padx=2, pady=2)
        #

        self.generate_button = ttk.Button(self.actions_frame, text="Generate")
        self.generate_button.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.EW)
        self.generate_button.bind("<Button-1>", self.generate)
        ##

    def run(self):
        sv_ttk.set_theme("dark")
        self.root.mainloop()