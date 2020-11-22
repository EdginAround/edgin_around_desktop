import socket, threading

import marshmallow

from edgin_around_api import actions, defs
from . import animations, animator, utils

from typing import List, Optional


class ConnectorThread(threading.Thread):
    """Thread for handling messages coming from the server."""

    def __init__(
        self, sock: socket.socket, event: threading.Event, animator: animator.Animator
    ) -> None:
        super().__init__()
        self._sock = sock
        self._event = event
        self._animator = animator
        self._processor = utils.SocketProcessor()

    def run(self) -> None:
        while self._event.is_set():
            messages = self._processor.read_messages(self._sock)
            for message in messages:
                self._process_message(message)

    def _process_message(self, message: str) -> None:
        """Converts the message to an `Animation` and passes it to the `Animator`."""

        action = actions.action_from_json_string(message)
        if action is None:
            return

        animation = animations.animation_from_action(action)
        if animation is None:
            return

        self._animator.add(animation)


class Connector:
    """Prepares and manages the thread handling messages from the server."""

    def __init__(self, animator: animator.Animator) -> None:
        self._event = threading.Event()
        self._animator = animator
        self._thread: Optional[ConnectorThread] = None

    def start(self, address: str) -> socket.socket:
        """
        Connects to the server pointed by the passed address and starts a thread processing
        incoming messages.
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, defs.PORT_DATA))

        self._thread = ConnectorThread(sock, self._event, self._animator)

        self._event.set()
        self._thread.start()

        return sock

    def stop(self) -> None:
        """Stops the thread. Waits until the thread is stopped."""

        self._event.clear()
        if self._thread is not None:
            self._thread.join()
