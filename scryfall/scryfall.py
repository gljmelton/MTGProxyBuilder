import msgspec
import requests
from .card import Card, Layout
from rapidfuzz import fuzz
from PIL import Image
from io import BytesIO
from enum import Enum

SEARCH_RATIO = 60

class Faces(Enum):
    Front = 0
    Back = 1

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
        print(f"[Scryfall][get_card_image] requesting card image {self.get_card_image_uri(card)}")
        headers = {
            "User-Agent": "ProxyBuilder",
            "Accept": "*/*"
        }
        response = requests.get(self.get_card_image_uri(card), headers=headers)

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
            if card.layout == Layout.ART_SERIES:
                continue

            ratio = fuzz.ratio(name.lower(), self.get_card_name(card).lower())
            if ratio >= SEARCH_RATIO and ratio > best_score:
                print(f"[Scryfall][search_by_name] Found better card: {self.get_card_name(card)}")
                best_score = ratio
                search_result = card

        return search_result

    @staticmethod
    def get_card_name(card, face: Faces= Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].name
        else :
            return card.name

    @staticmethod
    def get_card_image_uri(card: Card, face:Faces = Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].image_uris.normal
        else :
            return card.image_uris.normal

    @staticmethod
    def get_card_oracle(card: Card, face: Faces = Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].oracle_text
        else :
            return card.oracle_text

    @staticmethod
    def get_type_line(card: Card, face: Faces = Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].type_line
        else :
            return card.type_line

    @staticmethod
    def get_mana_value(card: Card, face: Faces = Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].mana_cost
        else :
            return card.mana_cost

    @staticmethod
    def get_power(card: Card, face: Faces = Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].power
        else :
            return card.power

    @staticmethod
    def get_toughness(card: Card, face: Faces = Faces.Front):
        if card.card_faces:
            return card.card_faces[face.value].toughness
        else :
            return card.toughness
