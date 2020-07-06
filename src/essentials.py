import random
import time

from math import pi

from abc import abstractmethod
from typing import List, Optional, Union, TYPE_CHECKING

from . import actions, defs, events, features, geometry
if TYPE_CHECKING: from . import state


EntityId = int


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
        self._num_calls = 0
        self._prev_call_time = time.monotonic()

    def get_num_calls(self) -> int:
        return self._num_calls

    def get_prev_call_time(self) -> float:
        return self._prev_call_time

    def perform(self, entity: 'Entity', state: 'state.State') -> JobResult:
        result = self.execute(entity, state)
        self._num_calls += 1
        self._prev_call_time = time.monotonic()
        return result

    @abstractmethod
    def get_start_delay(self) -> float: pass

    @abstractmethod
    def execute(self, entity: 'Entity', state: 'state.State') -> JobResult: pass


class Task:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def start(self, state: 'state.State') -> List[actions.Action]: pass

    @abstractmethod
    def finish(self, state: 'state.State') -> List[actions.Action]: pass

    @abstractmethod
    def get_job(self) -> Optional[Job]: pass


class IdleTask(Task):
    def __init__(self) -> None:
        super().__init__()

    def start(self, state: 'state.State') -> List[actions.Action]:
        return list()

    def finish(self, state: 'state.State') -> List[actions.Action]:
        return list()

    def get_job(self) -> Optional[Job]:
        return None


class Entity:
    def __init__(self, id: defs.ActorId, position: geometry.Point) -> None:
        self.id = id
        self.position: Optional[geometry.Point] = position
        self.task: Task = IdleTask()
        self.features = features.Features()

    def get_id(self) -> EntityId:
        return self.id

    def get_task(self) -> Task:
        return self.task

    def get_position(self) -> Optional[geometry.Point]:
        return self.position

    def set_position(self, position: Optional[geometry.Point]):
        self.position = position

    def move_by(self, distance, bearing, radius) -> None:
        if self.position is not None:
            self.position = self.position.moved_by(distance, bearing, radius)

    @abstractmethod
    def get_name(self) -> str: pass

    @abstractmethod
    def handle_event(self, event): pass

