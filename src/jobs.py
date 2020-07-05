from typing import List, Optional

from . import actions, defs, essentials, events, state


class HungerDrainJob(essentials.Job):
    INTERVAL = 1.0 # sec

    def __init__(self) -> None:
        super().__init__()

    def get_start_delay(self) -> float:
        return self.INTERVAL

    def perform(self, entity: essentials.Entity, state: state.State) -> essentials.JobResult:
        if entity.features.eater is None:
            return essentials.JobResult(list(), None)

        entity.features.eater.deduce(1.0)
        stats = entity.features.eater.gather_stats()
        action_list: List[actions.Action] = [actions.StatUpdateAction(entity.get_id(), stats)]
        return essentials.JobResult(action_list, self.INTERVAL)

    def __str__(self) -> str:
        return f'HungerDrainJob()'

    def __eq__(self, other) -> bool:
        return True


class MovementJob(essentials.Job):
    def __init__(self, duration: float, repeat: Optional[events.Event]) -> None:
        super().__init__()
        self.duration = duration
        self.repeat = repeat

    def get_start_delay(self) -> float:
        return self.duration

    def perform(self, entity: essentials.Entity, state: state.State) -> essentials.JobResult:
        return essentials.JobResult(list(), self.repeat)

    def __str__(self) -> str:
        return f'MovementJob(duration={self.duration}, repeat={self.repeat})'

    def __eq__(self, other) -> bool:
        return self.duration == other.duration \
           and self.repeat == other.repeat


class PickItemJob(essentials.Job):
    MAX_DISTANCE = 1.5 # XXX

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

    def get_start_delay(self) -> float:
        return self.duration

    def perform(self, entity: essentials.Entity, state: state.State) -> essentials.JobResult:
        noop = essentials.JobResult(list(), None)

        item = state.get_entity(self.what)
        if item is None:
            return noop

        if self.MAX_DISTANCE < state.get_distance(entity, item):
            return noop

        if not entity.features.inventory or not item.features.inventorable:
            return noop

        entity.features.inventory.store(self.hand, item.get_id(), item.get_name())
        item.features.inventorable.set_stored_by(entity.get_id())
        item.position = None

        action_list = [
                actions.PickEndAction(who=self.who, what=self.what),
                actions.UpdateInventoryAction(entity.features.inventory.get()),
                actions.DeleteActorsAction([self.what]),
            ]
        return essentials.JobResult(action_list, None)

    def __str__(self) -> str:
        return f'PickItemJob(who={self.who}, what={self.what}, duration={self.duration})'

    def __eq__(self, other) -> bool:
        return self.duration == other.duration

