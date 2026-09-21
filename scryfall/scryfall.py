import msgspec
import requests
from .card import Card
from rapidfuzz import fuzz
from PIL import Image
from io import BytesIO

SEARCH_RATIO = 60

class Scryfall:
    def __init__(self, bulk_data_path):
        self.bulk_data = None
        self.load_bulk_data(bulk_data_path)
        pass

    def load_bulk_data(self, bulk_data_path):
        self.bulk_data = []
        with open(bulk_data_path, 'rb') as file:
            for line in file:
                card = msgspec.json.decode(line, type=Card, strict=False)
                self.bulk_data.append(card)

    #HTTP
    def get_card_image(self, card : Card):
        print(f"[Scryfall][get_card_image] requesting card image {card.image_uris.normal}")
        headers = {
            "User-Agent": "ProxyBuilder",
            "Accept": "*/*"
        }
        response = requests.get(card.image_uris.normal, headers=headers)

        if response.status_code != 200:
            print(f"[Scryfall][get_card_image] Failed to get card image | Response: {response.status_code}")
            return None

        print("[Scryfall][get_card_image] Found card image")
        return response.content

    #For testing
    def get_first_card(self):
        return self.bulk_data[0]

    def search_by_name(self, name):
        search_result = None
        best_score = 0
        for card in self.bulk_data:
            ratio = fuzz.ratio(name.lower(), card.name.lower())
            if ratio >= SEARCH_RATIO and ratio > best_score:
                print(f"[Scryfall][search_by_name] Found better card: {card.name}")
                best_score = ratio
                search_result = card

        return search_result