from __future__ import annotations

from bs4 import BeautifulSoup, Tag


def create_tag(tag_type: str, **attributes: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    tag = soup.new_tag(tag_type)
    for key, value in attributes.items():
        if key == "class_":
            tag["class"] = value
        elif key == "inner_text":
            tag.string = value
        else:
            tag[key] = value
    return tag


def create_right_col_name(name: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Card Name:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    value_tag.string = name
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_expansion(expansion: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Expansion:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    first_a_tag = soup.new_tag("a")
    second_a_tag = soup.new_tag("a")
    second_a_tag.string = expansion
    value_tag.append(first_a_tag)
    value_tag.append(second_a_tag)
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_types(types: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Types:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    value_tag.string = types
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_mana_cost(cost: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Mana Cost:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    for char in cost:
        if char == "B":
            img_tag = soup.new_tag("img", alt="Black")
        elif char == "G":
            img_tag = soup.new_tag("img", alt="Green")
        elif char == "R":
            img_tag = soup.new_tag("img", alt="Red")
        elif char == "U":
            img_tag = soup.new_tag("img", alt="Blue")
        elif char == "W":
            img_tag = soup.new_tag("img", alt="White")
        else:
            img_tag = soup.new_tag("img", alt=char)
        value_tag.append(img_tag)
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_color_indicator(indicators: list[str]) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Color Indicator:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    value_tag.string = ", ".join(indicators)
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_rules(rules: list[str]) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Card Text:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    for rule in rules:
        rule_tag = soup.new_tag("div", attrs={"class": "cardtextbox"})
        rule_tag.string = rule
        value_tag.append(rule_tag)
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_loyalty(loyalty: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "Loyalty:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    value_tag.string = loyalty
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col_heft(power: str, toughness: str) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    row = soup.new_tag("div", attrs={"class": "row"})
    label_tag = soup.new_tag("div", attrs={"class": "label"})
    label_tag.string = "P/T:"
    value_tag = soup.new_tag("div", attrs={"class": "value"})
    value_tag.string = f"{power} / {toughness}"
    row.append(label_tag)
    row.append(value_tag)
    return row


def create_right_col(
    *,
    name: str,
    types: str,
    expansion: str,
    color_indicator: list[str] | None = None,
    loyalty: str | None = None,
    rules: list[str] | None = None,
    mana_cost: str | None = None,
    power: str | None = None,
    toughness: str | None = None,
) -> Tag:
    soup = BeautifulSoup("", "html.parser")
    tag = soup.new_tag("div", attrs={"class": "rightCol"})
    tag.append(create_right_col_name(name))
    tag.append(create_right_col_expansion(expansion))
    tag.append(create_right_col_types(types))
    if mana_cost is not None:
        tag.append(create_right_col_mana_cost(mana_cost))
    if color_indicator is not None:
        tag.append(create_right_col_color_indicator(color_indicator))
    if loyalty is not None:
        tag.append(create_right_col_loyalty(loyalty))
    if rules is not None:
        tag.append(create_right_col_rules(rules))
    if power is not None or toughness is not None:
        if power is None:
            power = ""
        if toughness is None:
            toughness = ""
        tag.append(create_right_col_heft(power, toughness))
    return tag
