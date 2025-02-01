from bs4.element import Tag


class ParseError(ValueError):
    """Base class for parsing errors."""


class MissingAttributeError(ParseError):
    def __init__(self, tag: Tag, attr_name: str) -> None:
        msg = f"Failed to parse tag: {tag}, expected a `{attr_name}` attribute"
        super().__init__(msg)


class MissingTagError(ParseError):
    def __init__(self, tag: Tag, tag_name: str) -> None:
        msg = f"Failed to parse tag: {tag}, missing `{tag_name}` tag"
        super().__init__(msg)
