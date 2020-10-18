import unittest

from typing import Any, Dict

from . import common

from src import actions

class ActionsTest(common.SerdeTest):
    def test_serde_delete_actors(self) -> None:
        """Test serialisation and deserialisation of DeleteActorsAction."""

        original: Dict[str, Any] = {
            'type': 'delete_actors',
            'actor_ids': [1, 4, 2],
        }

        self.assert_serde(original, actions.ActionSchema(), actions.DeleteActorsAction)

    def test_serde_damage(self) -> None:
        """Test serialisation and deserialisation of DamageAction."""

        original: Dict[str, Any] = {
            'type': 'damage',
            'dealer_id': 3,
            'receiver_id': 8,
            'variant': 'CHOP',
            'hand': 'RIGHT',
        }

        self.assert_serde(original, actions.ActionSchema(), actions.DamageAction)

    def test_serde_stat_update(self) -> None:
        """Test serialisation and deserialisation of StatUpdateAction."""

        original: Dict[str, Any] = {
            'type': 'stat_update',
            'actor_id': 3,
            'stats': {
                'hunger': 40.0,
                'max_hunger': 100.0,
            }
        }

        self.assert_serde(original, actions.ActionSchema(), actions.StatUpdateAction)

        d='{"actor_id": 0, "stats": {"hunger": 0.0, "max_hunger": 100.0}, "type": "stat_update"}'

    def test_serde_to_string(self) -> None:
        """Test if `Action.to_string` works correctly."""

        action = actions.MovementAction(
            actor_id=0,
            speed=7.0,
            bearing=30.0,
            duration=1.0,
        )

        string = action.to_string()
        self.assertTrue('"actor_id": 0' in string)
        self.assertTrue('"bearing": 30.0' in string)
        self.assertTrue('"duration": 1.0' in string)
        self.assertTrue('"speed": 7.0' in string)
        self.assertTrue('"type": "movement"' in string)

