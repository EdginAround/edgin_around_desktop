from typing import Optional

from . import actions, animator, defs, engine, events

class Proxy:
    def __init__(self) -> None:
        self.engine: Optional[engine.Engine] = None
        self.animator: Optional[animator.Animator] = None

    def send_action(self, action: actions.Action) -> None:
        if self.animator is not None:
            self.animator.add(action.into_animation())

    def send_event(self, event: events.Event) -> None:
        if self.engine is not None:
            self.engine.handle_event(0, event)

    def set_ends(self, engine, animator) -> None:
        self.engine = engine
        self.animator = animator

        if self.engine is not None:
            self.engine.handle_connection(0)

    def start_moving(self, bearing) -> None:
        self.send_event(events.StartMovingEvent(bearing))

    def stop_moving(self) -> None:
        self.send_event(events.StopMovingEvent())

    def activate_hand(self, hand: defs.Hand, item_id: defs.ActorId) -> None:
        self.send_event(events.HandActivationEvent(hand, item_id))

