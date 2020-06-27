from typing import Optional

from . import actions, animator, engine, events

class Proxy:
    def __init__(self) -> None:
        self.engine: Optional[engine.Engine] = None
        self.animator: Optional[animator.Animator] = None

    def send_action(self, action: actions.Action) -> None:
        if self.animator is not None:
            self.animator.add(action.into_animation())

    def set_ends(self, engine, animator) -> None:
        self.engine = engine
        self.animator = animator

        if self.engine is not None:
            self.engine.handle_event(events.ConnectionEvent())
