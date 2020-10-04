from abc import abstractmethod
from typing import List

from . import defs, geometry, inventory, scene

class Action:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return 'Action'


class ConfigurationAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'configuration'
    SERIALIZATION_FIELDS = ['hero_actor_id', 'elevation_function']

    def __init__(self, hero_actor_id: int, elevation_function: geometry.ElevationFunction) -> None:
        super().__init__()
        self.hero_actor_id = hero_actor_id
        self.elevation_function = elevation_function


class CreateActorsAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'create_actors'
    SERIALIZATION_FIELDS = ['actors']

    def __init__(self, actors: List[scene.Actor]) -> None:
        super().__init__()
        self.actors = actors


class DeleteActorsAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'delete_actors'
    SERIALIZATION_FIELDS = ['actors_ids']

    def __init__(self, actor_ids: List[defs.ActorId]) -> None:
        super().__init__()
        self.actor_ids = actor_ids


class MovementAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'movement'
    SERIALIZATION_FIELDS = ['actors_id', 'speed', 'bearing', 'duration']

    def __init__(self, actor_id, speed: float, bearing: float, duration: float) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.speed = speed
        self.bearing = bearing
        self.duration = duration


class LocalizeAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'localize'
    SERIALIZATION_FIELDS = ['actor_id', 'position']

    def __init__(self, actor_id: defs.ActorId, position: geometry.Point) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.position = position


class StatUpdateAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'stat_update'
    SERIALIZATION_FIELDS = ['actor_id', 'stats']

    def __init__(self, actor_id: defs.ActorId, stats: defs.Stats) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.stats = stats


class PickStartAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'pick_start'
    SERIALIZATION_FIELDS = ['who', 'what']

    def __init__(self, who: defs.ActorId, what: defs.ActorId) -> None:
        super().__init__()
        self.who = who
        self.what = what


class PickEndAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'pick_end'
    SERIALIZATION_FIELDS = ['who']

    def __init__(self, who: defs.ActorId) -> None:
        super().__init__()
        self.who = who


class UpdateInventoryAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'update_inventory'
    SERIALIZATION_FIELDS = ['owner_id', 'inventory']

    def __init__(self, owner_id: defs.ActorId, inventory: inventory.Inventory) -> None:
        super().__init__()
        self.owner_id = owner_id
        self.inventory = inventory


class DamageAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'damage'
    SERIALIZATION_FIELDS = ['dealer_id', 'receiver_id', 'variant', 'hand']

    def __init__(
            self,
            dealer_id: defs.ActorId,
            receiver_id: defs.ActorId,
            variant: defs.DamageVariant,
            hand: defs.Hand,
        ) -> None:
        super().__init__()
        self.dealer_id = dealer_id
        self.receiver_id = receiver_id
        self.variant = variant
        self.hand = hand


class CraftStartAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'craft_start'
    SERIALIZATION_FIELDS = ['crafter_id']

    def __init__(self, crafter_id: defs.ActorId) -> None:
        super().__init__()
        self.crafter_id = crafter_id


class CraftEndAction(Action, defs.Serializable):
    SERIALIZATION_NAME = 'craft_end'
    SERIALIZATION_FIELDS = ['crafter_id']

    def __init__(self, crafter_id: defs.ActorId) -> None:
        super().__init__()
        self.crafter_id = crafter_id

