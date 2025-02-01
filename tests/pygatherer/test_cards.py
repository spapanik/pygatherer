from http import HTTPStatus
from unittest import mock

import pytest

from pygatherer.cards import get_card_by_id


@mock.patch("pygatherer.cards.parse_gatherer_content")
@mock.patch("requests.get")
def test_get_card_valid_multiverse_id(
    mock_get: mock.MagicMock, mock_parse: mock.MagicMock
) -> None:
    mock_response = mock.MagicMock(status_code=HTTPStatus.OK, content=b"html content")
    mock_get.return_value = mock_response

    get_card_by_id(1)

    assert mock_get.call_count == 1
    assert mock_parse.call_count == 1


@mock.patch("pygatherer.cards.parse_gatherer_content")
@mock.patch("requests.get")
def test_get_card_invalid_multiverse_id(
    mock_get: mock.MagicMock, mock_parse: mock.MagicMock
) -> None:
    mock_response = mock.MagicMock(
        status_code=HTTPStatus.MULTIPLE_CHOICES, content=b"html content"
    )
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="No card with multiverse"):
        get_card_by_id(-1)

    assert mock_get.call_count == 1
    assert mock_parse.call_count == 0
