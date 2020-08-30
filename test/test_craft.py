import unittest

from src import craft

class CraftTest(unittest.TestCase):
    def test_ingredient_filter_items(self) -> None:
        """Checks if filtering works correctly. Filtered list should contain only items compatible
        with the given ingredient/material."""

        ingredient = craft.Ingredient(craft.Material.WOOD, 1)

        input_items = {
            craft.Item(0, craft.Essence.ROCKS, 1),
            craft.Item(1, craft.Essence.LOGS, 1),
        }

        expected_items = {
            craft.Item(1, craft.Essence.LOGS, 1),
        }

        result_items = ingredient.filter_items(input_items)
        self.assertEqual(result_items, expected_items)

    def test_assembly_filter_items(self) -> None:
        """Checks if filtering works correctly. Quantities of items in the filtered list should be
        reduced by quantities of corresponding items/entities in the assembly. If the new quantity
        is zero, the item should be removed."""

        assembly = craft.Assembly(
            recipe_codename='test_recipe',
            sources=[
                [craft.Item(0, craft.Essence.ROCKS, 2), craft.Item(4, craft.Essence.ROCKS, 3)],
                [craft.Item(3, craft.Essence.STICKS, 3), craft.Item(1, craft.Essence.LOGS, 2)],
            ],
        )

        input_items = {
            craft.Item(0, craft.Essence.ROCKS, 3),
            craft.Item(1, craft.Essence.LOGS, 2),
            craft.Item(2, craft.Essence.GOLD, 2),
        }

        expected_items = {
            craft.Item(0, craft.Essence.ROCKS, 1),
            craft.Item(2, craft.Essence.GOLD, 2),
        }

        result_items = assembly.filter_items(input_items)
        self.assertEqual(result_items, expected_items)

    def test_assembly_find_item(self) -> None:
        """Checks if items lookup in `Assembly` works correctly."""

        rocks1 = craft.Item(0, craft.Essence.ROCKS, 2)
        rocks2 = craft.Item(4, craft.Essence.ROCKS, 3)
        sticks = craft.Item(3, craft.Essence.STICKS, 3)
        logs = craft.Item(1, craft.Essence.LOGS, 2)

        assembly = craft.Assembly(
            recipe_codename='test_recipe',
            sources=[[rocks1, rocks2], [sticks, logs]],
        )

        self.assertEqual(assembly.find_item(3, None), sticks)
        self.assertEqual(assembly.find_item(3, 0), None)
        self.assertEqual(assembly.find_item(5, None), None)

    def test_assembly_update_item(self) -> None:
        """Updating the assembly items should work correctly."""

        assembly = craft.Assembly(
            recipe_codename='test_recipe',
            sources=[[
                craft.Item(1, craft.Essence.GOLD, 3),
                craft.Item(2, craft.Essence.LOGS, 3),
                craft.Item(3, craft.Essence.STICKS, 3),
            ], []],
        )

        expected = craft.Assembly(
            recipe_codename='test_recipe',
            sources=[[
                craft.Item(1, craft.Essence.GOLD, 2),
                craft.Item(2, craft.Essence.LOGS, 5),
                craft.Item(3, craft.Essence.STICKS, 3),
                craft.Item(4, craft.Essence.ROCKS, 2),
            ], []],
        )

        # Negative change on not existing item is a noop
        self.assertFalse(assembly.update_item(1, craft.Item(3, craft.Essence.STICKS, 0), -1))

        # Removing too many existing items is a noop
        self.assertFalse(assembly.update_item(0, craft.Item(3, craft.Essence.STICKS, 0), -5))

        # Increasing quantity of not existing items should create them
        self.assertTrue(assembly.update_item(0, craft.Item(4, craft.Essence.ROCKS, 0), 2))

        # Increasing quantity of existing items should work correctly
        self.assertTrue(assembly.update_item(0, craft.Item(2, craft.Essence.LOGS, 0), 2))

        # Increasing quantity of existing items should work correctly
        self.assertTrue(assembly.update_item(0, craft.Item(1, craft.Essence.GOLD, 0), -1))

        self.assertEqual(assembly, expected)

