import time

from typing import Iterable, List, Optional

from . import defs, dials, inventory, scene


class Animation:
    def __init__(self, timeout):
        self._expired = False
        self.start_time = time.monotonic()
        self.timeout = timeout

    def expired(self) -> bool:
        if self._expired:
            return True

        elif self.timeout is not None:
            return self.start_time + self.timeout < time.monotonic()

        else:
            return False

    # If a newly added action returns an actor ID, it cancels and replaces any other action assigned
    # to the same actor.
    def get_actor_id(self) -> Optional[defs.ActorId]:
        return None

    def expire(self) -> None:
        self._expired = True

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        raise NotImplementedError('This animation is not implemented')


class ConfigurationAnimation(Animation):
    def __init__(self, hero_actor_id: int, elevation_function) -> None:
        super().__init__(None)
        self.hero_actor_id = hero_actor_id
        self.elevation_function = elevation_function

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        scene.configure(self.hero_actor_id, self.elevation_function)
        self.expire()


class CreateActorsAnimation(Animation):
    def __init__(self, actors: List[scene.Actor]) -> None:
        super().__init__(None)
        self.actors = actors

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        scene.create_actors(self.actors)
        self.expire()


class DeleteActorsAnimation(Animation):
    def __init__(self, actor_ids: List[defs.ActorId]) -> None:
        super().__init__(None)
        self.actor_ids = actor_ids

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        scene.delete_actors(self.actor_ids)
        self.expire()


class MovementAnimation(Animation):
    def __init__(self, timeout, actor_id: defs.ActorId, bearing, speed) -> None:
        super().__init__(timeout)
        self.actor_id = actor_id
        self.bearing = bearing
        self.speed = speed

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        distance = self.speed * tick_interval
        actor = scene.get_actor(self.actor_id)
        actor.move_by(distance, self.bearing, scene.get_radius())


class LocalizeAnimation(Animation):
    def __init__(self, actor_id: defs.ActorId) -> None:
        super().__init__(None)
        self.actor_id = actor_id

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        self.expire()


class StatUpdateAnimation(Animation):
    def __init__(self, actor_id, stats: defs.Stats) -> None:
        super().__init__(None)
        self.actor_id = actor_id
        self.stats = stats

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        actor = scene.get_actor(self.actor_id)
        dials.set_stats(self.stats)
        self.expire()


class PickStartAnimation(Animation):
    def __init__(self, actor_id: defs.ActorId, item_id: defs.ActorId) -> None:
        super().__init__(None)
        self.actor_id = actor_id
        self.item_id = item_id

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        # TODO: Implement animations and plays pick animation here
        self.expire()


class PickEndAnimation(Animation):
    def __init__(self, actor_id: defs.ActorId, item_id: defs.ActorId) -> None:
        super().__init__(None)
        self.actor_id = actor_id
        self.item_id = item_id

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        # TODO: Implement animations and plays pick animation here
        self.expire()


class UpdateInventoryAnimation(Animation):
    def __init__(self, inventory: inventory.Inventory) -> None:
        super().__init__(None)
        self.inventory = inventory

    def tick(self, tick_interval, scene: scene.Scene, dials: dials.Dials) -> None:
        dials.set_inventory(self.inventory)
        self.expire()

