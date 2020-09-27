import unittest

from typing import Final

from src import craft, defs, inventory

class InventoryTest(unittest.TestCase):
    def test_capasity(self) -> None:
        entry = inventory.InventoryEntry(0, craft.Essence.ROCKS, 1, '')
        self.assertEqual(entry.calc_max_quantity_for_item_volume(20), 5)
        self.assertEqual(entry.calc_max_quantity_for_item_volume(22), 4)

    def test_to_items(self) -> None:
        inv = inventory.Inventory()
        inv.store(defs.Hand.LEFT, id=1, essence=craft.Essence.ROCKS, quantity=1, codename='')
        inv.store(defs.Hand.RIGHT, id=2, essence=craft.Essence.LOGS, quantity=2, codename='')

        expected = {
            craft.Item(actor_id=1, essence=craft.Essence.ROCKS, quantity=1),
            craft.Item(actor_id=2, essence=craft.Essence.LOGS, quantity=2),
        }

        result = inv.to_items()
        self.assertEqual(result, expected)

    def test_swap(self) -> None:
        INDEX: Final[int] = 0

        inv = inventory.Inventory()
        inv.store(defs.Hand.LEFT, id=1, essence=craft.Essence.ROCKS, quantity=1, codename='')
        inv.store(defs.Hand.RIGHT, id=2, essence=craft.Essence.LOGS, quantity=2, codename='')
        inv.insert(INDEX, id=3, essence=craft.Essence.GOLD, quantity=2, codename='')

        inv.swap(defs.Hand.LEFT, INDEX)

        self.assertEqual(inv.get_hand(defs.Hand.LEFT), 3)
        self.assertEqual(inv.get_hand(defs.Hand.RIGHT), 2)
        self.assertEqual(inv.get_pocket(INDEX), 1)

    def test_remove_with_entity_id(self) -> None:
        inv = inventory.Inventory()
        inv.store(defs.Hand.LEFT, id=1, essence=craft.Essence.ROCKS, quantity=1, codename='')
        inv.store(defs.Hand.RIGHT, id=2, essence=craft.Essence.LOGS, quantity=2, codename='')

        expected = {
            craft.Item(actor_id=2, essence=craft.Essence.LOGS, quantity=2),
        }

        inv.remove_with_entity_id(1)
        result = inv.to_items()
        self.assertEqual(result, expected)



