from typing import Optional

from . import defs


class InventoryEntry:
    def __init__(self, id: defs.ActorId, image: str) -> None:
        self.id = id
        self.image = image


class Inventory:
    def __init__(self):
        self.left_hand: Optional[InventoryEntry] = None
        self.right_hand: Optional[InventoryEntry] = None

    def get_hand(self, hand: defs.Hand) -> Optional[defs.ActorId]:
        if hand == defs.Hand.LEFT:
            return self.left_hand.id if self.left_hand else None
        elif hand == defs.Hand.RIGHT:
            return self.right_hand.id if self.right_hand else None
        else:
            return None

    def store(self, hand: defs.Hand, id: defs.ActorId, image: str):
        entry = InventoryEntry(id, image)
        if hand == defs.Hand.LEFT:
            self.left_hand = entry
        elif hand == defs.Hand.RIGHT:
            self.right_hand = entry

