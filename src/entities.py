import random

from math import pi

from . import actions, defs, essentials, events, features, geometry, tasks


class Rocks(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: geometry.Point) -> None:
        super().__init__(id, position)
        self.features.inventorable = features.InventorableFeature()

    def get_name(self) -> str:
        return 'rocks'

    def handle_event(self, event: events.Event) -> None:
        pass


class Axe(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: geometry.Point) -> None:
        super().__init__(id, position)
        self.features.inventorable = features.InventorableFeature()

    def get_name(self) -> str:
        return 'axe'

    def handle_event(self, event: events.Event) -> None:
        pass


class Warior(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: geometry.Point) -> None:
        super().__init__(id, position)
        self.features.performer = features.PerformerFeature()

    def get_name(self) -> str:
        return 'warior'

    def handle_event(self, event: events.Event) -> None:
        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            bearing = random.uniform(-pi, pi)
            self.task = tasks.WalkTask(self.get_id(), speed=1.0, bearing=bearing, duration=1.0)


class Hero(essentials.Entity):
    PICK_TIMEOUT = 1.0 # seconds

    def __init__(self, id: defs.ActorId, position: geometry.Point) -> None:
        self.task: essentials.Task
        super().__init__(id, position)
        self.features.eater = features.EaterFeature(max_capacity=100.0, hunger_value=50.0)
        self.features.inventory = features.InventoryFeature()

    def get_name(self) -> str:
        return 'hero'

    def handle_event(self, event: events.Event) -> None:
        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            self.task = essentials.IdleTask()

        elif isinstance(event, events.StartMovingEvent):
            self.task = tasks.MovementTask(self.get_id(), speed=1.0, bearing=event.bearing)

        elif isinstance(event, events.StopMovingEvent):
            self.task = essentials.IdleTask()

        elif isinstance(event, events.HandActivationEvent):
            self.task = tasks.PickItemTask(
                    self.get_id(),
                    event.item_id,
                    event.hand,
                    duration=self.PICK_TIMEOUT,
                )

