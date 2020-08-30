import unittest

from src import craft, defs, inventory

class InventoryTest(unittest.TestCase):
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

