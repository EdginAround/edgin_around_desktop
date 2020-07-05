import random

from math import pi

from . import actions, essentials, events, features, tasks


class Rocks(essentials.Entity):
    def __init__(self, id, position) -> None:
        super().__init__(id, position)
        self.features.inventorable = features.InventorableFeature()

    def get_name(self) -> str:
        return 'rocks'


class Axe(essentials.Entity):
    def __init__(self, id, position) -> None:
        super().__init__(id, position)
        self.features.inventorable = features.InventorableFeature()

    def get_name(self) -> str:
        return 'axe'


class Warior(essentials.Entity):
    def __init__(self, id, position) -> None:
        super().__init__(id, position)
        self.features.performer = features.PerformerFeature()

    def get_name(self) -> str:
        return 'warior'

    def handle_event(self, event: events.Event) -> essentials.EventResult:
        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            bearing = random.uniform(-pi, pi)
            self.task = tasks.WalkTask(self.get_id(), bearing=bearing, duration=1.0, speed=1.0)

        return essentials.EventResult(None, self.task.get_job(), self.task.get_action())


class Hero(essentials.Entity):
    PICK_TIMEOUT = 1.0 # seconds

    def __init__(self, id, position) -> None:
        self.task: essentials.Task
        super().__init__(id, position)
        self.features.eater = features.EaterFeature(max_capacity=100.0, hunger_value=50.0)
        self.features.inventory = features.InventoryFeature()

    def get_name(self) -> str:
        return 'hero'

    def handle_event(self, event: events.Event) -> essentials.EventResult:
        final_action = None

        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            self.task = essentials.IdleTask()

        elif isinstance(event, events.StartMovingEvent):
            self.task = tasks.MovementTask(self.get_id(), bearing=event.bearing, speed=1.0)

        elif isinstance(event, events.StopMovingEvent):
            final_action = actions.LocalizeAction(self.get_id())
            self.task = essentials.IdleTask()

        elif isinstance(event, events.HandActivationEvent):
            self.task = tasks.PickItemTask(
                    self.get_id(),
                    event.item_id,
                    event.hand,
                    duration=self.PICK_TIMEOUT,
                )

        return essentials.EventResult(final_action, self.task.get_job(), self.task.get_action())

