import time

from typing import List, Optional

from . import actions, defs, essentials, events, state


class WaitJob(essentials.Job):
    def __init__(self, duration: float, repeat: Optional[events.Event]) -> None:
        super().__init__()
        self.duration = duration
        self.repeat = repeat

    def get_start_delay(self) -> float:
        return self.duration

    def execute(self, entity: essentials.Entity, state: state.State) -> essentials.JobResult:
        return essentials.JobResult(list(), self.repeat)

    def __str__(self) -> str:
        return f'WaitJob(duration={self.duration}, repeat={self.repeat})'

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and self.duration == other.duration


class HungerDrainJob(essentials.Job):
    INTERVAL = 1.0 # sec

    def __init__(self) -> None:
        super().__init__()

    def get_start_delay(self) -> float:
        return self.INTERVAL

    def execute(self, entity: essentials.Entity, state: state.State) -> essentials.JobResult:
        if entity.features.eater is None:
            return essentials.JobResult(list(), None)

        entity.features.eater.deduce(1.0)
        stats = entity.features.eater.gather_stats()
        action_list: List[actions.Action] = [actions.StatUpdateAction(entity.get_id(), stats)]
        return essentials.JobResult(action_list, self.INTERVAL)

    def __str__(self) -> str:
        return f'HungerDrainJob()'

    def __eq__(self, other) -> bool:
        return type(self) == type(other)


class MovementJob(essentials.Job):
    INTERVAL = 0.1 # second

    def __init__(
            self,
            speed: float,
            bearing: float,
            duration: float,
            finish_event: Optional[events.Event],
        ) -> None:
        super().__init__()
        self.speed = speed
        self.bearing = bearing
        self.duration = duration
        self.finish_event = finish_event
        self.start_time = time.monotonic()

    def get_start_delay(self) -> float:
        return self.INTERVAL

    def execute(self, entity: essentials.Entity, state: state.State) -> essentials.JobResult:
        entity.move_by(self.speed * self.INTERVAL, self.bearing, state.get_radius())

        now = time.monotonic()
        if self.start_time + self.duration < now:
            return essentials.JobResult(list(), self.finish_event)
        else:
            return essentials.JobResult(list(), self.INTERVAL)

    def __str__(self) -> str:
        return f'MovementJob(speed={self.speed}, bearing={self.bearing}, duration={self.duration})'

    def __eq__(self, other) -> bool:
        return type(self) == type(other) \
           and self.speed == other.speed \
           and self.bearing == other.bearing \
           and self.duration == other.duration

