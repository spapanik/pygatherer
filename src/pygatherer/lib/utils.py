from enum import Enum
from functools import lru_cache


class BaseEnum(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,  # noqa: ARG004
        count: int,  # noqa: ARG004
        last_values: list[str],  # noqa: ARG004
    ) -> str:
        return name.replace("_", " ").title()

    @classmethod
    @lru_cache
    def values(cls) -> set[str]:
        return {member.value for member in cls.__members__.values()}
