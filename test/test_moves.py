import unittest

from typing import Any, Dict

from . import common

from src import moves

class CraftTest(common.SerdeTest):
    def test_serde_stop(self) -> None:
        """Test serialisation and deserialisation of StopMove."""

        original: Dict[str, Any] = {
            'type': 'stop',
        }

        self.assert_serde(original, moves.MoveSchema(), moves.StopMove)

    def test_serde_hand_activation(self) -> None:
        """Test serialisation and deserialisation of HandActivationMove."""

        original: Dict[str, Any] = {
            'type': 'hand_activation',
            'hand': 'LEFT',
            'object_id': 4,
        }

        self.assert_serde(original, moves.MoveSchema(), moves.HandActivationMove)

