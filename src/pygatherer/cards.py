from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup
from pathurl import Query

from pygatherer.lib.constants import CARD_DETAILS_URL, FALSE_TAG
from pygatherer.lib.content_parser import parse_gatherer_content

if TYPE_CHECKING:
    from pygatherer.lib.models import Card


def get_card_by_id(multiverse_id: int) -> Card:
    gatherer_url = CARD_DETAILS_URL.replace(
        query=Query.from_dict(multiverseid=str(multiverse_id))
    )

    response = requests.get(
        gatherer_url.string, allow_redirects=False, timeout=(60, 120)
    )
    if response.status_code >= HTTPStatus.MULTIPLE_CHOICES:
        msg = f"No card with multiverse_id {multiverse_id} exists"
        raise ValueError(msg)
    content = response.content.decode("utf-8")
    soup = BeautifulSoup(re.sub(FALSE_TAG, "", content, count=1), "lxml")
    return parse_gatherer_content(soup, multiverse_id)
