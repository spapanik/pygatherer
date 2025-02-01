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
