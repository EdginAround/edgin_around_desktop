import unittest

from typing import Any, Dict, Final

from src import craft, defs, inventory

class InventoryTest(unittest.TestCase):
    def test_capasity(self) -> None:
        entry = inventory.EntityInfo(0, craft.Essence.ROCKS, 1, 1, '')
        self.assertEqual(entry.calc_max_quantity_for_item_volume(20), 5)
        self.assertEqual(entry.calc_max_quantity_for_item_volume(22), 4)

    def test_to_items(self) -> None:
        inv = inventory.Inventory()
        inv.store(
            defs.Hand.LEFT,
            id=1,
            essence=craft.Essence.ROCKS,
            current_quantity=1,
            item_volume=1,
            codename='',
        )
        inv.store(
            defs.Hand.RIGHT,
            id=2,
            essence=craft.Essence.LOGS,
            current_quantity=2,
            item_volume=1,
            codename='',
        )

        expected = {
            craft.Item(actor_id=1, essence=craft.Essence.ROCKS, quantity=1),
            craft.Item(actor_id=2, essence=craft.Essence.LOGS, quantity=2),
        }

        result = inv.to_items()
        self.assertEqual(result, expected)

    def test_swap(self) -> None:
        INDEX: Final[int] = 0

        inv = inventory.Inventory()
        inv.store(
            defs.Hand.LEFT,
            id=1,
            essence=craft.Essence.ROCKS,
            current_quantity=1,
            item_volume=1,
            codename='',
        )
        inv.store(
            defs.Hand.RIGHT,
            id=2,
            essence=craft.Essence.LOGS,
            current_quantity=2,
            item_volume=1,
            codename='',
        )
        inv.insert(
            INDEX,
            id=3,
            essence=craft.Essence.GOLD,
            current_quantity=2,
            item_volume=1,
            codename='',
        )

        inv.swap(defs.Hand.LEFT, INDEX)

        self.assertEqual(inv.get_hand(defs.Hand.LEFT), 3)
        self.assertEqual(inv.get_hand(defs.Hand.RIGHT), 2)
        self.assertEqual(inv.get_pocket(INDEX), 1)

    def test_remove_with_entity_id(self) -> None:
        inv = inventory.Inventory()
        inv.store(
            defs.Hand.LEFT,
            id=1,
            essence=craft.Essence.ROCKS,
            current_quantity=1,
            item_volume=1,
            codename='',
        )
        inv.store(
            defs.Hand.RIGHT,
            id=2,
            essence=craft.Essence.LOGS,
            current_quantity=2,
            item_volume=1,
            codename='',
        )

        expected = {
            craft.Item(actor_id=2, essence=craft.Essence.LOGS, quantity=2),
        }

        inv.remove_with_entity_id(1)
        result = inv.to_items()
        self.assertEqual(result, expected)

    def test_serialization_empty(self) -> None:
        """
        Checks if the inventory is serialized and deserialized properly when the inventory is
        completely empty.
        """

        original: Dict[str, Any] = {
            'left_hand': None,
            'right_hand': None,
            'entries': 20 * [None],
        }

        schema = inventory.Inventory.Schema()
        inv = schema.load(original)
        self.assertEqual(type(inv), inventory.Inventory)
        parsed = schema.dump(inv)
        self.assertFalse('\n' in parsed)
        self.assertDictEqual(original, parsed)

    def test_serialization_filled(self) -> None:
        """
        Checks if the inventory is serialized and deserialized properly when the inventory is filled
        with items.
        """

        original:Dict[str, Any] = {
            'left_hand': {
                'id': 1,
                'essence': 'LOGS',
                'current_quantity': 1,
                'codename': 'log',
                'item_volume': 3,
            },
            'right_hand': {
                'id': 2,
                'essence': 'ROCKS',
                'current_quantity': 3,
                'codename': 'rocks',
                'item_volume': 5,
            },
            'entries': [
                None, None, None, None, None, None, None, None, None, {
                    'id': 3,
                    'essence': 'GOLD',
                    'current_quantity': 2,
                    'codename': 'gold',
                    'item_volume': 5,
                },
                None, None, None, None, None, None, None, None, None, None,
            ]
        }

        schema = inventory.Inventory.Schema()
        inv = schema.load(original)
        self.assertEqual(type(inv), inventory.Inventory)
        parsed = schema.dump(inv)
        self.assertFalse('\n' in parsed)
        self.assertDictEqual(original, parsed)

