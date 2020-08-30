import unittest

from typing import List

from src import craft, entities, essentials, geometry, inventory, state

class StateTest(unittest.TestCase):
    def test_craft(self) -> None:
        """
        Checks if crafting a item (axe) works correctly:
         * items used fully should be removed
         * not used items should not be touched
         * inventory should be updated
        """

        NUM_ROCK, NUM_GOLD, NUM_LOGS = 2, 2, 1

        elevation_function = geometry.ElevationFunction(1000)
        rock = entities.Rocks(1, None)
        gold = entities.Gold(2, None)
        logs = entities.Log(3, None)
        assert rock.features.stackable is not None
        assert gold.features.stackable is not None
        rock.features.stackable.set_size(NUM_ROCK)
        gold.features.stackable.set_size(NUM_GOLD)
        entity_list: List[essentials.Entity] = [rock, gold, logs]

        inv = inventory.Inventory()
        inv.insert(1, id=rock.id, essence=rock.ESSENCE, quantity=NUM_ROCK, codename='')
        inv.insert(2, id=gold.id, essence=gold.ESSENCE, quantity=NUM_GOLD, codename='')
        inv.insert(3, id=logs.id, essence=logs.ESSENCE, quantity=NUM_LOGS, codename='')

        st = state.State(elevation_function, entity_list)

        assembly = craft.Assembly(
            recipe_codename='axe',
            sources=[
                [craft.Item(actor_id=rock.id, essence=rock.ESSENCE, quantity=NUM_ROCK)],
                [craft.Item(actor_id=logs.id, essence=logs.ESSENCE, quantity=NUM_LOGS)],
            ]
        )

        result = st.craft_entity(assembly, inv)

        self.assertEqual(len(result.created), 1)
        self.assertEqual(set(result.deleted), {logs.id, rock.id})
        ents = list(st.get_entities())
        self.assertEqual(len(ents), 2)
        self.assertEqual(ents[0], gold)
        self.assertEqual(ents[1].get_name(), 'axe')

        axe = ents[1]

        result_items = inv.to_items()
        expected_items = {
                craft.Item(actor_id=gold.id, essence=gold.ESSENCE, quantity=NUM_GOLD),
                craft.Item(actor_id=axe.id, essence=axe.ESSENCE, quantity=1),
            }
        self.assertEqual(result_items, expected_items)

