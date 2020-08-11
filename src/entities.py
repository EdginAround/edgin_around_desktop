import random

from math import pi

from typing import List

from . import actions, defs, essentials, events, features, tasks


class Rocks(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: essentials.EntityPosition) -> None:
        super().__init__(id, position)
        self.features.set_inventorable()

    def get_name(self) -> str:
        return 'rocks'

    def handle_event(self, event: events.Event) -> None:
        pass


class Log(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: essentials.EntityPosition) -> None:
        super().__init__(id, position)
        self.features.set_inventorable()

    def get_name(self) -> str:
        return 'log'

    def handle_event(self, event: events.Event) -> None:
        pass


class Axe(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: essentials.EntityPosition) -> None:
        super().__init__(id, position)
        self.features.set_inventorable()
        self.features.set_tool_or_weapon(
                hit_damage=10,
                chop_damage=100,
                smash_damage=20,
                attack_damage=50,
            )

    def get_name(self) -> str:
        return 'axe'

    def handle_event(self, event: events.Event) -> None:
        pass


class Spruce(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: essentials.EntityPosition) -> None:
        super().__init__(id, position)
        self.features.set_damageable(
                start_health=200,
                max_health=400,
                damage_variant=defs.DamageVariant.CHOP,
            )

    def get_name(self) -> str:
        return 'spruce'

    def handle_event(self, event: events.Event) -> None:
        if isinstance(event, events.DamageEvent):
            assert self.features.damageable
            is_alive = self.features.damageable.handle_damage(event.damage_amount)
            if not is_alive:
                self.task = tasks.DieAndDrop(self.get_id(), self.generate_drops())

    def generate_drops(self) -> List[essentials.Entity]:
        assert self.position is not None
        return [Log(-1, self.position) for i in range(3)]

class Warrior(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: essentials.EntityPosition) -> None:
        super().__init__(id, position)
        self.features.set_performer()

    def get_name(self) -> str:
        return 'warrior'

    def handle_event(self, event: events.Event) -> None:
        if isinstance(event, events.ResumeEvent) or isinstance(event, events.FinishedEvent):
            bearing = random.uniform(-pi, pi)
            self.task = tasks.WalkTask(self.get_id(), speed=1.0, bearing=bearing, duration=1.0)


class Hero(essentials.Entity):
    def __init__(self, id: defs.ActorId, position: essentials.EntityPosition) -> None:
        self.task: essentials.Task
        super().__init__(id, position)
        self.features.set_inventory()
        self.features.set_eater(max_capacity=100.0, hunger_value=50.0)

    def get_name(self) -> str:
        return 'pirate'

    def handle_event(self, event: events.Event) -> None:
        assert self.features.inventory

        if isinstance(event, events.ConcludeEvent):
            self.task.conclude()

        elif isinstance(event, events.StopEvent) or isinstance(event, events.FinishedEvent):
            self.task = essentials.IdleTask()

        elif isinstance(event, events.StartMovingEvent):
            self.task = tasks.MovementTask(self.get_id(), speed=1.0, bearing=event.bearing)

        elif isinstance(event, events.HandActivationEvent):
            item_id = self.features.inventory.get().get_hand(event.hand)
            if item_id is not None:
                self.task = tasks.UseItemTask(self.get_id(), item_id, event.object_id)
            else:
                self.task = tasks.PickItemTask(self.get_id(), event.object_id, event.hand)

        elif isinstance(event, events.InventorySwapEvent):
            self.task = tasks.InventorySwapTask(self.get_id(), event.hand, event.inventory_index)

        elif isinstance(event, events.ResumeEvent):
            self.task = essentials.IdleTask()

