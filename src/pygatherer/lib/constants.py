import re
from enum import auto, unique

from pathurl import URL

from pygatherer.lib.utils import BaseEnum

BASE_URL = URL("https://gatherer.wizards.com/")
CARD_URL = BASE_URL.join("Pages/Card/")
CARD_DETAILS_URL = CARD_URL.join("Details.aspx")
CARD_IMAGE_URL = BASE_URL.join("Handlers/Image.ashx")
FALSE_TAG = re.compile(r"^<\?xml.*?\?>")


@unique
class Supertype(BaseEnum):
    BASIC = auto()
    LEGENDARY = auto()
    ONGOING = auto()
    SNOW = auto()
    WORLD = auto()
