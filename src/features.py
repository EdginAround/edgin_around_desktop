import random

from math import pi

from typing import Optional

from . import defs, inventory


class Feature:
    def __init__(self) -> None:
        pass

    def __bool__(self) -> bool:
        return True


class PerformerFeature(Feature):
    def __init__(self) -> None:
        super().__init__()

    def start(self):
        pass


class EatableFeature(Feature):
    def __init__(self) -> None:
        super().__init__()


class EaterFeature(Feature):
    def __init__(self, max_capacity: float, hunger_value: float) -> None:
        super().__init__()
        self.max_capacity = max_capacity
        self.hunger_value = hunger_value

    def deduce(self, value: float) -> None:
        self.hunger_value = max(self.hunger_value - value, 0.0)

    def get_hunger(self) -> float:
        return self.hunger_value

    def gather_stats(self) -> defs.Stats:
        return defs.Stats(hunger=self.hunger_value, max_hunger=self.max_capacity)


class InventoryFeature(Feature):
    def __init__(self) -> None:
        super().__init__()
        self.inventory = inventory.Inventory()

    def store(self, hand: defs.Hand, id: defs.ActorId, image: str) -> None:
        self.inventory.store(hand, id, image)

    def get(self) -> inventory.Inventory:
        return self.inventory


class InventorableFeature(Feature):
    def __init__(self) -> None:
        super().__init__()
        self.stored_by: Optional[defs.ActorId] = None

    def set_stored_by(self, id: defs.ActorId) -> None:
        self.stored_by = id


class Features:
    def __init__(self) -> None:
        self.performer: Optional[PerformerFeature] = None
        self.eatable: Optional[EatableFeature] = None
        self.eater: Optional[EaterFeature] = None
        self.inventory: Optional[InventoryFeature] = None
        self.inventorable: Optional[InventorableFeature] = None

