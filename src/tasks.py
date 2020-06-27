from typing import Optional

from . import actions

class Task:
    def __init__(self) -> None:
        pass

    def get_action(self) -> Optional[actions.Action]:
        return None

    def get_timeout(self) -> float:
        return 10.0


class IdleTask(Task):
    def __init__(self) -> None:
        super().__init__()


class WalkTask(Task):
    def __init__(self, entity_id, duration, bearing, speed) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.duration = duration
        self.bearing = bearing
        self.speed = speed

    def get_action(self) -> Optional[actions.Action]:
        return actions.MovementAction(self.entity_id, self.duration, self.bearing, self.speed)

    def get_timeout(self) -> float:
        return self.duration

