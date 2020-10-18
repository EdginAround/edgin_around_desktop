import abc, json
from dataclasses import dataclass

import marshmallow
from marshmallow import fields as mf
from marshmallow_enum import EnumField
from marshmallow_oneofschema import OneOfSchema

from typing import Optional, Sequence, cast

from . import craft, defs


class Move(abc.ABC):
    class Schema(marshmallow.Schema):
        pass

    def __init__(self) -> None:
        pass


@dataclass
class StopMove(Move):
    SERIALIZATION_NAME = 'stop'

    class Schema(marshmallow.Schema):
        @marshmallow.post_load
        def make(self, data, **kwargs):
            return StopMove(**data)


@dataclass
class ConcludeMove(Move, defs.Serializable):
    SERIALIZATION_NAME = 'conclude'

    class Schema(marshmallow.Schema):
        @marshmallow.post_load
        def make(self, data, **kwargs):
            return ConcludeMove(**data)


@dataclass
class StartMotionMove(Move, defs.Serializable):
    SERIALIZATION_NAME = 'start_motion'

    bearing: float

    class Schema(marshmallow.Schema):
        bearing = mf.Float()

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return StartMotionMove(**data)


@dataclass
class HandActivationMove(Move, defs.Serializable):
    SERIALIZATION_NAME = 'hand_activation'

    hand: defs.Hand
    object_id: Optional[defs.ActorId]

    class Schema(marshmallow.Schema):
        hand = EnumField(defs.Hand)
        object_id = mf.Integer()

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return HandActivationMove(**data)


@dataclass
class InventoryUpdateMove(Move, defs.Serializable):
    SERIALIZATION_NAME = 'inventory_update'

    hand: defs.Hand
    inventory_index: int
    update_variant: defs.UpdateVariant

    class Schema(marshmallow.Schema):
        hand = EnumField(defs.Hand)
        inventory_index = mf.Integer()
        update_variant = EnumField(defs.UpdateVariant)

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return InventoryUpdateMove(**data)


@dataclass
class CraftMove(Move, defs.Serializable):
    SERIALIZATION_NAME = 'craft'

    assembly: craft.Assembly

    class Schema(marshmallow.Schema):
        assembly = mf.Nested(craft.Assembly.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return CraftMove(**data)


_MOVES = cast(Sequence[defs.Serializable], (
    StopMove,
    ConcludeMove,
    StartMotionMove,
    HandActivationMove,
    InventoryUpdateMove,
    CraftMove,
))


class MoveSchema(OneOfSchema):
    """A schema for any type of action."""

    type_schemas = { cls.SERIALIZATION_NAME: cls.Schema for cls in _MOVES }
    type_names = { cls: cls.SERIALIZATION_NAME for cls in _MOVES }

    def get_obj_type(self, obj):
        name = self.type_names.get(type(obj), None)
        if name is not None:
            return name
        else:
            raise Exception("Unknown object type: {}".format(obj.__class__.__name__))


def move_from_json_string(string: str) -> Optional[Move]:
    """
    Converts a JSON string into a move.
    If conversion fails prints the reason and returns `None`.
    """

    try:
        data = json.loads(string)
        res = MoveSchema().load(data)
        return res
    except Exception as e:
        print(f'Move deserialisation failure: {e} - ({string})')
        return None

