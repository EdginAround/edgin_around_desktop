import random

from math import pi

from typing import List, Optional, Union, TYPE_CHECKING

from . import actions, events, features
if TYPE_CHECKING: from . import state


EntityId = int


class Task:
    def __init__(self) -> None:
        pass

    def get_action(self) -> Optional[actions.Action]:
        return None

    def get_job(self) -> Optional['Job']:
        return None


class IdleTask(Task):
    def __init__(self) -> None:
        super().__init__()


class EventResult:
    def __init__(
            self,
            final_action: Optional[actions.Action],
            next_job: Optional['Job'],
            next_action: Optional[actions.Action],
        ):
        self.final_action = final_action
        self.next_job = next_job
        self.next_action = next_action

    def __eq__(self, other):
        return self.final_action == other.final_action \
           and self.next_job == other.next_job \
           and self.next_action == self.next_action


class Entity:
    def __init__(self, id, position) -> None:
        self.id = id
        self.position = position
        self.task: Task = IdleTask()
        self.features = features.Features()

    def get_id(self) -> EntityId:
        return self.id

    def get_name(self) -> str:
        return ''

    def handle_event(self, event) -> EventResult:
        return EventResult(None, None, None)


class JobResult:
    def __init__(
            self,
            actions: List[actions.Action],
            repeat: Union[float, events.Event, None],
    ) -> None:
        self.actions = actions
        self.repeat = repeat


class Job:
    def __init__(self) -> None:
        pass

    def get_start_delay(self) -> float:
        return 0.0

    def perform(self, entity: Entity, state: 'state.State') -> JobResult:
        return JobResult(list(), None)

