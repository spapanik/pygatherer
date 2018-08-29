import urllib.parse

import requests
from bs4 import BeautifulSoup

from utils.constants import CARD_URL, SUPERTYPES


def parse_cost_image(cost_img):
    alt = cost_img["alt"]
    try:
        cost = int(alt)
    except ValueError:
        pass
    else:
        return {"type": "Colorless", "value": cost}

    if alt.startswith("Phyrexian"):
        _, color = alt.split()
        return {"type": "Phyrexian", "colors": [color]}

    if " or " in alt:
        first, second = alt.split(" or ")
        if first == "Two":
            return {"type": "Monocolored Hybrid", "colors": [second]}
        return {"type": "Hybrid", "colors": [first, second]}

    return {"type": "Colored", "colors": [alt]}


def parse_types(types):
    main_types, *subtypes = types.split("—")
    supertypes = []
    types = []
    for main_type in main_types.split():
        main_type.strip()
        if main_type in SUPERTYPES:
            supertypes.append(main_type)
        else:
            types.append(main_type)

    if subtypes:
        subtypes = subtypes[0]
        if "Plane" in types:
            subtypes = [subtypes.strip()]
        else:
            subtypes = [subtype.strip() for subtype in subtypes.split()]

    return supertypes, types, subtypes


def parse_cost(cost):
    cost_images = [
        parse_cost_image(cost_img) for cost_img in cost.select("img")
    ]
    return cost_images


def parse_rules(rules):
    return [rule.text for rule in rules.select("div.cardtextbox")]


def parse_pt(pt):
    power, toughness = pt.split("/")
    return power.strip(), toughness.strip()


def get_id_from_image_url(image_url):
    query = urllib.parse.urlparse(image_url).query
    return urllib.parse.parse_qs(query)["multiverseid"][0]


def parse_left_col(left_col):
    img = left_col.img
    image_url = urllib.parse.urljoin(CARD_URL, img["src"])
    multiverse_id = get_id_from_image_url(image_url)
    out = {"image_url": image_url, "multiverse_id": int(multiverse_id)}

    variations = [
        variation
        for variation in left_col.select_one("div.variations").select("a")
        if variation["id"] == multiverse_id
    ]
    if variations:
        out["variation"] = int(variations[0].text)

    return out


def parse_right_col(right_col):
    rows = {
        row.select_one(".label").text.strip(): row.select_one(".value")
        for row in right_col.select("div.row")
    }

    supertypes, types, subtypes = parse_types(rows["Types:"].text.strip())

    out = {
        "name": rows["Card Name:"].text.strip(),
        "expansion": rows["Expansion:"].select("a")[1].text.strip(),
        "supertypes": supertypes,
        "types": types,
        "subtypes": subtypes,
    }

    if "Mana Cost:" in rows:
        out["cost"] = parse_cost(rows["Mana Cost:"])

    if "Color Indicator:" in rows:
        out["color_indicator"] = [
            indication.strip()
            for indication in rows["Color Indicator:"].text.split(",")
        ]

    if "Loyalty:" in rows:
        out["loyalty"] = rows["Loyalty:"].text.strip()

    if "Card Text:" in rows:
        out["rules"] = parse_rules(rows["Card Text:"])

    if "P/T:" in rows:
        power, toughness = parse_pt(rows["P/T:"].text.strip())
        out["power"] = power
        out["toughness"] = toughness

    return out


class Card:
    def __init__(self, attributes):
        self.multiverse_id = attributes["multiverse_id"]
        self.image_url = attributes["image_url"]
        self.variation = attributes.get("variation")
        self.name = attributes["name"]
        self.expansion = attributes["expansion"]
        self.supertypes = attributes["supertypes"]
        self.types = attributes["types"]
        self.subtypes = attributes["subtypes"]
        self.cost = attributes.get("cost")
        self.color_indicator = attributes.get("color_indicator")
        self.loyalty = attributes.get("loyalty")
        self.rules = attributes.get("rules")
        self.power = attributes.get("power")
        self.toughness = attributes.get("toughness")

    def __str__(self):
        return self.name

    def __dict__(self):
        return {
            "multiverse_id": self.multiverse_id,
            "image_url": self.image_url,
            "variation": self.variation,
            "name": self.name,
            "expansion": self.expansion,
            "supertypes": self.supertypes,
            "types": self.types,
            "subtypes": self.subtypes,
            "cost": self.cost,
            "color_indicator": self.color_indicator,
            "loyalty": self.loyalty,
            "rules": self.rules,
            "power": self.power,
            "toughness": self.toughness,
        }


class CardParser:
    __slots__ = ["multiverse_id", "url", "card", "faces"]

    def __init__(self, multiverse_id):
        self.multiverse_id = multiverse_id
        self.url = f"{CARD_URL}Details.aspx?multiverseid={multiverse_id}"
        self._update_attributes()

    def _update_attributes(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "lxml")
        faces_table = soup.select_one("table.cardComponentTable")
        faces = faces_table.select("table.cardDetails")
        self.faces = {}
        for face in faces:
            right_col = face.select_one("td.rightCol")
            left_col = face.select_one("td.leftCol")
            if left_col is None:
                left_col = face.select_one("td.plane")

            attributes = {
                **parse_left_col(left_col),
                **parse_right_col(right_col),
            }
            card = Card(attributes)
            self.faces[card.multiverse_id] = card.name
            if card.multiverse_id == self.multiverse_id:
                self.card = card
