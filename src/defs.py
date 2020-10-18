import json
from enum import Enum

import marshmallow
from marshmallow import fields as mf

from typing import Any, Dict, Final, List, NoReturn, Union


ActorId = int

VERSION = (0, 0, 1)
PORT_BROADCAST = 54300
PORT_DATA = 54301
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
    HIT = 'hit'
    CHOP = 'chop'
    SMASH = 'smash'
    ATTACK = 'attack'


class UpdateVariant(Enum):
    """Generic enum describing type of item stack update."""

    SWAP = 0
    MERGE = 1


class Attachement(Enum):
    LEFT_ITEM = 'left_item'
    RIGHT_ITEM = 'right_item'


class Stats:
    class Schema(marshmallow.Schema):
        hunger = mf.Float()
        max_hunger = mf.Float()

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return Stats(**data)

    def __init__(self, hunger: float, max_hunger: float) -> None:
        self.hunger = hunger
        self.max_hunger = max_hunger


class Debugable:
    DEBUG_FIELDS: List[str] = list()

    def __str__(self) -> str:
        fields = {field: str(getattr(self, field)) for field in self.DEBUG_FIELDS}
        return f'{type(self).__name__}{fields}'


class Serializable:
    SERIALIZATION_NAME: str = '___'

    class Schema(marshmallow.Schema):
        pass

    def to_dict(self) -> Dict[str, Any]:
        result = self.Schema().dump(self)
        result[SERIALIZATION_TYPE_FIELD] = self.SERIALIZATION_NAME
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


def assert_exhaustive(x: NoReturn) -> NoReturn:
    assert False, "Unhandled type: {}".format(type(x).__name__)

