from enum import Enum

from typing import List, NoReturn


ActorId = int


INVENTORY_SIZE: int = 20


class Hand(Enum):
    LEFT = 0
    RIGHT = 1


class DamageVariant(Enum):
    HIT = 0
    CHOP = 1
    SMASH = 2
    ATTACK = 3


class Stats:
    def __init__(self, hunger, max_hunger) -> None:
        self.hunger = hunger
        self.max_hunger = max_hunger


class Debugable:
    DEBUG_FIELDS: List[str] = list()

    def __str__(self) -> str:
        fields = {field: str(getattr(self, field)) for field in self.DEBUG_FIELDS}
        return f'{type(self).__name__}{fields}'


def assert_exhaustive(x: NoReturn) -> NoReturn:
    assert False, "Unhandled type: {}".format(type(x).__name__)

