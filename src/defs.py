import json
from enum import Enum

from typing import Any, Dict, Final, List, NoReturn, Union


ActorId = int

INVENTORY_SIZE: int = 20
SERIALIZATION_TYPE_FIELD = '_type'
UNASSIGNED_ACTOR_ID: Final[ActorId] = -1


class Hand(Enum):
    LEFT = 0
    RIGHT = 1

    def other(self):
        if self == Hand.LEFT:
            return Hand.RIGHT
        else:
            return Hand.LEFT


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


class Serializable:
    SERIALIZATION_NAME: str = '___'
    SERIALIZATION_FIELDS: List[str] = list()

    def to_dict(self) -> Dict[str, Any]:
        fields: Dict[str, Any] = {SERIALIZATION_TYPE_FIELD: self.SERIALIZATION_NAME}
        for field in self.SERIALIZATION_FIELDS:
            value = getattr(self, field)
            if isinstance(value, Serializable):
                fields[field] = value.to_dict()
            else:
                fields[field] = str(value)
        return fields

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


def assert_exhaustive(x: NoReturn) -> NoReturn:
    assert False, "Unhandled type: {}".format(type(x).__name__)

