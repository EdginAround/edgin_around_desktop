from typing import Optional

from . import actions, animations, animator, craft, defs, engine, events


class Proxy:
    CLIENT_ID = 0

    def __init__(self) -> None:
        self.engine: Optional[engine.Engine] = None
        self.animator: Optional[animator.Animator] = None

    def send_action(self, action: actions.Action) -> None:
        if self.animator is not None:
            animation = animations.animation_from_action(action)
            if animation is not None:
                self.animator.add(animation)

    def set_ends(self, engine, animator) -> None:
        self.engine = engine
        self.animator = animator

        assert self.engine is not None
        self.engine.handle_connection(self.CLIENT_ID)

    def send_stop(self) -> None:
        assert self.engine is not None
        if (receiver_id := self.engine.get_hero_id_for_client(self.CLIENT_ID)) is not None:
            self._send_event(events.StopEvent(receiver_id))

    def send_conclude(self) -> None:
        assert self.engine is not None
        if (receiver_id := self.engine.get_hero_id_for_client(self.CLIENT_ID)) is not None:
            self._send_event(events.ConcludeEvent(receiver_id))

    def send_move(self, bearing) -> None:
        assert self.engine is not None
        if (receiver_id := self.engine.get_hero_id_for_client(self.CLIENT_ID)) is not None:
            self._send_event(events.StartMovingEvent(receiver_id, bearing))

    def send_hand(self, hand: defs.Hand, item_id: Optional[defs.ActorId]) -> None:
        assert self.engine is not None
        if (receiver_id := self.engine.get_hero_id_for_client(self.CLIENT_ID)) is not None:
            self._send_event(events.HandActivationEvent(receiver_id, hand, item_id))

    def send_inventory_swap(self, hand: defs.Hand, inventory_index: int) -> None:
        assert self.engine is not None
        if (receiver_id := self.engine.get_hero_id_for_client(self.CLIENT_ID)) is not None:
            self._send_event(events.InventorySwapEvent(receiver_id, hand, inventory_index))

    def send_craft(self, assembly: craft.Assembly) -> None:
        assert self.engine is not None
        if (receiver_id := self.engine.get_hero_id_for_client(self.CLIENT_ID)) is not None:
            self._send_event(events.CraftEvent(receiver_id, assembly))

    def _send_event(self, event: events.Event) -> None:
        assert self.engine is not None
        self.engine.handle_event(event)

