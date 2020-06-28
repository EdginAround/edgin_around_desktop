import random

from math import pi

from typing import Optional, Tuple

from . import actions, events, tasks


class PerformerFeature:
    def __init__(self, brain) -> None:
        self.brain = brain

    def start(self):
        pass


class EatableFeature:
    def __init__(self) -> None:
        pass


class Features:
    def __init__(self) -> None:
        self.performer: Optional[PerformerFeature] = None
        self.eatable: Optional[EatableFeature] = None


class Entity:
    def __init__(self, id, position) -> None:
        self.id = id
        self.position = position
        self.task: tasks.Task = tasks.IdleTask()
        self.features = Features()

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return ''

    def get_task(self) -> tasks.Task:
        return self.task

    def handle_event(self, event) -> Tuple[Optional[actions.Action], tasks.Task]:
        return None, self.task


class Brain:
    def __init__(self) -> None:
        pass

    def on_event(self, event):
        return IdleAction()


class WariorBrain:
    def __init__(self) -> None:
        super().__init__()

    def on_event(self, event, entity_id) -> tasks.Task:
        return tasks.WalkTask(entity_id, bearing=random.uniform(-pi, pi), duration=5, speed=5)


class Warior(Entity):
    def __init__(self, id, position) -> None:
        super().__init__(id, position)
        self.features.performer = PerformerFeature(WariorBrain())

    def get_name(self) -> str:
        return 'warior'

    def handle_event(self, event: events.Event) -> Tuple[Optional[actions.Action], tasks.Task]:
        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            bearing = random.uniform(-pi, pi)
            self.task = tasks.WalkTask(self.get_id(), bearing=bearing, duration=1.0, speed=1.0)

        return None, self.task


class Hero(Entity):
    LONG_TIMEOUT = 20.0 # seconds

    def __init__(self, id, position) -> None:
        super().__init__(id, position)

    def get_name(self) -> str:
        return 'hero'

    def handle_event(self, event: events.Event) -> Tuple[Optional[actions.Action], tasks.Task]:
        action = None

        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            self.task = tasks.IdleTask()

        elif isinstance(event, events.StartMovingEvent):
            self.task = tasks.WalkTask(
                    self.get_id(),
                    bearing=event.bearing,
                    duration=Hero.LONG_TIMEOUT,
                    speed=1.0,
                )

        elif isinstance(event, events.StopMovingEvent):
            action = actions.LocalizeAction(self.get_id())
            self.task = tasks.IdleTask()

        return action, self.task

