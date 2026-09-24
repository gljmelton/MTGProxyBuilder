import scryfall
from scryfall.scryfall import Scryfall
from app_interface import BuilderApp
from layout_generator import LayoutGenerator
from scryfall.card import Card

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

class ProxyBuilder:
    def __init__(self):

        self.layout_generator = LayoutGenerator()
        self.app = BuilderApp(self.layout_generator.get_fonts())
        self.app.search_callback = self.search_card
        self.app.generate_callback = self.generate_layout
        self.app.font_preview_callback = self.generate_font_preview
        self.scryfall_data = Scryfall("oracle-cards.jsonl")
        self.search_result : Card | None = None

    def run(self):
        self.app.run()

    def search_card(self, search_term):
        self.app.push_status("Searching...", "white")
        result = self.scryfall_data.search_by_name(search_term)

        if result is None:
            self.app.push_status("No card found!", "red")
            print(f"No result found!")
            return

        print(f"[ProxyBuilder][search_card] Search results: {result.name}")
        self.search_result = result
        self.app.update_search_result(self.scryfall_data.get_card_image(result))
        self.app.push_status("Card found!", "green")

    def generate_layout(self, custom_data):
        self.app.push_status("Generating...", "white")
        result = self.layout_generator.generate(custom_data, self.search_result)
        if not result:
            self.app.push_status("Unable to generate!", "red")

        else:
            self.app.push_status("Generator success!", "green")

    def generate_font_preview(self):
        self.app.push_status("Generating font preview...", "white")
        result_img = self.layout_generator.generate_preview()
        if not result_img:
            self.app.push_status("Unable to generate!", "red")

        else:
            self.app.push_status("Generator success!", "green")
            self.app.update_font_preview()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = ProxyBuilder()
    app.run()
