from typing import Optional

from . import actions, defs, essentials, events, jobs


class MovementTask(essentials.Task):
    TIMEOUT = 20.0 # seconds

    def __init__(self, entity_id, bearing, speed) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.bearing = bearing
        self.speed = speed

    def get_action(self) -> Optional[actions.Action]:
        return actions.MovementAction(self.entity_id, self.TIMEOUT, self.bearing, self.speed)

    def get_job(self) -> Optional[essentials.Job]:
        return jobs.MovementJob(self.TIMEOUT, None)


class WalkTask(essentials.Task):
    def __init__(self, entity_id, duration, bearing, speed) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.duration = duration
        self.bearing = bearing
        self.speed = speed

    def get_action(self) -> Optional[actions.Action]:
        return actions.MovementAction(self.entity_id, self.duration, self.bearing, self.speed)

    def get_job(self) -> Optional[essentials.Job]:
        return jobs.MovementJob(self.duration, events.FinishedEvent())


class PickItemTask(essentials.Task):
    def __init__(
            self,
            who: essentials.EntityId,
            what: essentials.EntityId,
            hand: defs.Hand,
            duration: float,
        ) -> None:
        super().__init__()
        self.who = who
        self.what = what
        self.hand = hand
        self.duration = duration

    def get_action(self) -> Optional[actions.Action]:
        return actions.PickStartAction(self.who, self.what)

    def get_job(self) -> Optional[essentials.Job]:
        return jobs.PickItemJob(self.who, self.what, self.hand, self.duration)

