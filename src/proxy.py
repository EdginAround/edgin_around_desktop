import json, socket

from typing import Optional

from edgin_around_api import craft, defs, moves


class Proxy:
    """Provides an interface to send messages to the server."""

    def __init__(self) -> None:
        self._sock: Optional[socket.socket] = None
        self._schema = moves.MoveSchema()

    def set_socket(self, sock: socket.socket) -> None:
        """Set the socket to be used."""

        self._sock = sock

    def send_stop(self) -> None:
        """Send `stop` move."""

        self._send_move(moves.MotionStopMove())

    def send_motion(self, bearing) -> None:
        """Send `motion` move."""

        self._send_move(moves.MotionStartMove(bearing))

    def send_hand_activation(self, hand: defs.Hand, item_id: Optional[defs.ActorId]) -> None:
        """Send `hand_activation` move."""

        self._send_move(moves.HandActivationMove(hand, item_id))

    def send_inventory_swap(self, hand: defs.Hand, inventory_index: int) -> None:
        """Send `swap` variant of `inventory_update` move."""

        self._send_move(
            moves.InventoryUpdateMove(
                hand,
                inventory_index,
                defs.UpdateVariant.SWAP,
            )
        )

    def send_inventory_merge(self, hand: defs.Hand, inventory_index: int) -> None:
        """Send `merge` variant of `inventory_update` move."""

        self._send_move(
            moves.InventoryUpdateMove(
                hand,
                inventory_index,
                defs.UpdateVariant.MERGE,
            )
        )

    def send_craft(self, assembly: craft.Assembly) -> None:
        """Send `craft` move."""

        self._send_move(moves.CraftMove(assembly))

    def _send_move(self, move: moves.Move) -> None:
        """Send the given move to the server."""

        if self._sock is not None:
            string = json.dumps(self._schema.dump(move)) + "\n"
            self._sock.sendall(string.encode())
