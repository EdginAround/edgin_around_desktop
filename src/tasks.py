import time

from typing import List, Optional

from . import actions, defs, essentials, events, jobs, state


class MovementTask(essentials.Task):
    TIMEOUT = 20.0 # seconds

    def __init__(self, entity_id: defs.ActorId, speed: float, bearing: float) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.speed = speed
        self.bearing = bearing
        self.job = jobs.MovementJob(self.speed, self.bearing, self.TIMEOUT, None)

    def start(self, state: state.State) -> List[actions.Action]:
        return [actions.MovementAction(self.entity_id, self.speed, self.bearing, self.TIMEOUT)]

    def get_job(self) -> Optional[essentials.Job]:
        return self.job

    def finish(self, state: state.State) -> List[actions.Action]:
        entity = state.get_entity(self.entity_id)
        assert entity is not None

        interval = time.monotonic() - self.job.get_prev_call_time()
        entity.move_by(self.speed * interval, self.bearing, state.get_radius())

        position = entity.get_position()
        assert position is not None
        return [actions.LocalizeAction(self.entity_id, position)]


class WalkTask(essentials.Task):
    def __init__(
            self,
            entity_id: defs.ActorId,
            speed: float,
            bearing: float,
            duration: float,
        ) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.speed = speed
        self.bearing = bearing
        self.duration = duration

    def start(self, state: state.State) -> List[actions.Action]:
        return [actions.MovementAction(self.entity_id, self.speed, self.bearing, self.duration)]

    def get_job(self) -> Optional[essentials.Job]:
        return jobs.MovementJob(self.speed, self.bearing, self.duration, events.FinishedEvent())

    def finish(self, state: state.State) -> List[actions.Action]:
        entity = state.get_entity(self.entity_id)
        assert entity is not None
        position = entity.get_position()
        assert position is not None
        return [actions.LocalizeAction(self.entity_id, position)]


class PickItemTask(essentials.Task):
    MAX_DISTANCE = 1.0

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

    def start(self, state: state.State) -> List[actions.Action]:
        return [actions.PickStartAction(self.who, self.what)]

    def get_job(self) -> Optional[essentials.Job]:
        return jobs.WaitJob(self.duration, events.FinishedEvent())

    def finish(self, state: state.State) -> List[actions.Action]:
        entity = state.get_entity(self.who)
        item = state.get_entity(self.what)
        if entity is None or item is None:
            return list()

        if not entity.features.inventory or not item.features.inventorable:
            return list()

        distance = state.get_distance(entity, item)
        if distance is None or self.MAX_DISTANCE < distance:
            return list()

        entity.features.inventory.store(self.hand, item.get_id(), item.get_name())
        item.features.inventorable.set_stored_by(entity.get_id())
        item.set_position(None)

        return [
                actions.PickEndAction(who=self.who, what=self.what),
                actions.UpdateInventoryAction(entity.features.inventory.get()),
                actions.DeleteActorsAction([self.what]),
            ]

