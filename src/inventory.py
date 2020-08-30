from typing import List, Optional, Set

from . import craft, defs


class InventoryEntry:
    def __init__(self,
            id: defs.ActorId,
            essence: craft.Essence,
            quantity: int,
            codename: str,
        ) -> None:
        self.id = id
        self.essence = essence
        self.quantity = quantity
        self.codename = codename

    def to_item(self) -> craft.Item:
        return craft.Item(self.id, self.essence, self.quantity)

    def __repr__(self) -> str:
        return f'InventoryEntry(' \
            f'id={self.id}, essence={self.essence.get_description()}, ' \
            f'quantity={self.quantity}, codename={self.codename})'


class Inventory:
    def __init__(self) -> None:
        self.left_hand: Optional[InventoryEntry] = None
        self.right_hand: Optional[InventoryEntry] = None
        self.entries: List[Optional[InventoryEntry]] = [None for i in range(defs.INVENTORY_SIZE)]

    def get_hand(self, hand: defs.Hand) -> Optional[defs.ActorId]:
        if hand == defs.Hand.LEFT:
            return self.left_hand.id if self.left_hand else None
        elif hand == defs.Hand.RIGHT:
            return self.right_hand.id if self.right_hand else None
        else:
            return None

    def store(
            self,
            hand: defs.Hand,
            id: defs.ActorId,
            essence: craft.Essence,
            quantity: int,
            codename: str,
        ) -> None:
        entry = InventoryEntry(id, essence, quantity, codename)
        if hand == defs.Hand.LEFT:
            self.left_hand = entry
        elif hand == defs.Hand.RIGHT:
            self.right_hand = entry

    def insert(
            self,
            index: int,
            id: defs.ActorId,
            essence: craft.Essence,
            quantity: int,
            codename: str,
        ) -> None:
        self.entries[index] = InventoryEntry(id, essence, quantity, codename)

    def swap(self, hand: defs.Hand, index: int) -> None:
        if index < defs.INVENTORY_SIZE:
            entry = self.entries[index]
            if hand == defs.Hand.LEFT:
                self.entries[index] = self.left_hand
                self.left_hand = entry
            elif hand == defs.Hand.RIGHT:
                self.entries[index] = self.right_hand
                self.right_hand = entry

    def to_items(self) -> Set[craft.Item]:
        result: Set[craft.Item] = set()

        if self.left_hand is not None:
            result.add(self.left_hand.to_item())

        if self.right_hand is not None:
            result.add(self.right_hand.to_item())

        for entry in self.entries:
            if entry is not None:
                result.add(entry.to_item())

        return result

    def get_free_hand(self, prefered=defs.Hand.RIGHT) -> Optional[defs.Hand]:
        hand = None
        if self.get_hand(prefered) is None:
            hand = defs.Hand.LEFT
        elif self.get_hand(prefered.other()) is None:
            hand = defs.Hand.RIGHT
        return hand

    def find_entity_with_entity_id(self, entity_id: defs.ActorId) -> Optional[InventoryEntry]:
        if self.left_hand is not None and self.left_hand.id == entity_id:
            return self.left_hand

        if self.right_hand is not None and self.right_hand.id == entity_id:
            return self.right_hand

        for entry in self.entries:
            if entry is not None and entry.id == entity_id:
                return entry

        return None

    def remove_with_entity_id(self, entity_id: defs.ActorId) -> None:
        if self.left_hand is not None and self.left_hand.id == entity_id:
            self.left_hand = None
            return

        if self.right_hand is not None and self.right_hand.id == entity_id:
            self.right_hand = None
            return

        for i, entry in enumerate(self.entries):
            if entry is not None and entry.id == entity_id:
                self.entries[i] = None
                return

