from typing import List, Optional, Set

from . import craft, defs, settings


class EntityInfo:
    """Displayable info about an entity."""

    MAX_VOLUME = settings.Sizes.HUGE.value

    def __init__(self,
            id: defs.ActorId,
            essence: craft.Essence,
            current_quantity: int,
            item_volume: int,
            codename: str,
        ) -> None:
        self.id = id
        self.essence = essence
        self.current_quantity = current_quantity
        self.codename = codename
        self.max_quantity = self.calc_max_quantity_for_item_volume(item_volume)

    def to_item(self) -> craft.Item:
        return craft.Item(self.id, self.essence, self.current_quantity)

    def calc_max_quantity_for_item_volume(self, item_volume: int) -> int:
        """
        Calculates how many items with given volume `item_volume` can fit into the pocket/stack
        represented by this `EntityInfo`.
        """

        return int(self.MAX_VOLUME / item_volume)

    def set_quantity(self, quantity: int) -> None:
        self.current_quantity = quantity

    def __repr__(self) -> str:
        return f'EntityInfo(' \
            f'id={self.id}, essence={self.essence.get_description()}, ' \
            f'current_quantity={self.current_quantity}, max_quantity={self.max_quantity}, ' \
            f'codename={self.codename})'


class Inventory:
    def __init__(self) -> None:
        self.left_hand: Optional[EntityInfo] = None
        self.right_hand: Optional[EntityInfo] = None
        self.entries: List[Optional[EntityInfo]] = [None for i in range(defs.INVENTORY_SIZE)]

    def get_hand(self, hand: defs.Hand) -> Optional[defs.ActorId]:
        if hand == defs.Hand.LEFT:
            return self.left_hand.id if self.left_hand else None
        elif hand == defs.Hand.RIGHT:
            return self.right_hand.id if self.right_hand else None
        else:
            return None

    def get_hand_entry(self, hand: defs.Hand) -> Optional[EntityInfo]:
        if hand == defs.Hand.LEFT:
            return self.left_hand
        else:
            return self.right_hand

    def get_pocket(self, index: int) -> Optional[defs.ActorId]:
        if self.is_index_valid(index):
            entry = self.entries[index]
            return entry.id if entry is not None else None
        else:
            return None

    def get_pocket_entry(self, index: int) -> Optional[EntityInfo]:
        return self.entries[index] if self.is_index_valid(index) else None

    def store(
            self,
            hand: defs.Hand,
            id: defs.ActorId,
            essence: craft.Essence,
            current_quantity: int,
            item_volume: int,
            codename: str,
        ) -> None:
        entry = EntityInfo(id, essence, current_quantity, item_volume, codename)
        self.store_entry(hand, entry)

    def store_entry(self, hand: defs.Hand, entry: EntityInfo) -> None:
        if hand == defs.Hand.LEFT:
            self.left_hand = entry
        elif hand == defs.Hand.RIGHT:
            self.right_hand = entry

    def insert(
            self,
            index: int,
            id: defs.ActorId,
            essence: craft.Essence,
            current_quantity: int,
            item_volume: int,
            codename: str,
        ) -> None:
        entry = EntityInfo(id, essence, current_quantity, item_volume, codename)
        self.insert_entry(index, entry)

    def insert_entry(self, index: int, entry: EntityInfo) -> None:
        if self.is_index_valid(index):
            self.entries[index] = entry

    def swap(self, hand: defs.Hand, index: int) -> None:
        if self.is_index_valid(index):
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

    def find_entity_with_entity_id(self, entity_id: defs.ActorId) -> Optional[EntityInfo]:
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

    def is_index_valid(self, index: int) -> bool:
        return -1 < index and index < defs.INVENTORY_SIZE

