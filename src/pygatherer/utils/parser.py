import urllib.parse

import requests
from bs4 import BeautifulSoup

from pygatherer.utils.constants import CARD_URL, SUPERTYPES


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
    return [parse_cost_image(cost_img) for cost_img in cost.select("img")]


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
    variation = None
    variations = [
        variation
        for variation in left_col.select_one("div.variations").select("a")
        if variation["id"] == multiverse_id
    ]

    if variations:
        variation: int(variations[0].text)

    return {
        "image_url": image_url,
        "multiverse_id": int(multiverse_id),
        "variation": variation,
    }


def parse_right_col(right_col):
    rows = {
        row.select_one(".label").text.strip(): row.select_one(".value")
        for row in right_col.select("div.row")
    }
    supertypes, types, subtypes = parse_types(rows["Types:"].text.strip())
    cost = color_indicator = loyalty = rules = power = toughness = None

    if "Mana Cost:" in rows:
        cost = parse_cost(rows["Mana Cost:"])

    if "Color Indicator:" in rows:
        color_indicator = [
            indication.strip()
            for indication in rows["Color Indicator:"].text.split(",")
        ]

    if "Loyalty:" in rows:
        loyalty = rows["Loyalty:"].text.strip()

    if "Card Text:" in rows:
        rules = parse_rules(rows["Card Text:"])

    if "P/T:" in rows:
        power, toughness = parse_pt(rows["P/T:"].text.strip())

    return {
        "name": rows["Card Name:"].text.strip(),
        "expansion": rows["Expansion:"].select("a")[1].text.strip(),
        "supertypes": supertypes,
        "types": types,
        "subtypes": subtypes,
        "cost": cost,
        "color_indicator": color_indicator,
        "loyalty": loyalty,
        "rules": rules,
        "power": power,
        "toughness": toughness,
    }


def parse_gatherer_content(content):
    soup = BeautifulSoup(content, "lxml")
    url = soup.select_one("form#aspnetForm")["action"]
    multiverse_id = int(get_id_from_image_url(url))
    faces_table = soup.select_one("table.cardComponentTable")
    faces = faces_table.select("table.cardDetails")
    for face in faces:
        right_col = face.select_one("td.rightCol")
        left_col = face.select_one("td.leftCol")
        if left_col is None:
            left_col = face.select_one("td.plane")

        card_info = {**parse_left_col(left_col), **parse_right_col(right_col)}
        if card_info["multiverse_id"] == multiverse_id:
            return card_info


def get_card_by_id(multiverse_id):
    gatherer_url = f"{CARD_URL}Details.aspx?multiverseid={multiverse_id}"

    response = requests.get(gatherer_url, allow_redirects=False)
    if response.status_code >= 300:
        raise ValueError(f"No card with multiverse_id {multiverse_id} exists")
    return parse_gatherer_content(response.content)
