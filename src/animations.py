import time

from abc import abstractmethod
from typing import Iterable, List, Optional

from . import defs, dials, geometry, inventory, scene, world


class AnimationName:
    IDLE = 'idle'
    WALK = 'walk'
    PICK = 'pick'


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

    @abstractmethod
    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        raise NotImplementedError('This animation is not implemented')


class ConfigurationAnimation(Animation):
    def __init__(self, hero_actor_id: int, elevation_function) -> None:
        super().__init__(None)
        self.hero_actor_id = hero_actor_id
        self.elevation_function = elevation_function

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        scene.configure(self.hero_actor_id, self.elevation_function)
        self.expire()


class CreateActorsAnimation(Animation):
    def __init__(self, actors: List[scene.Actor]) -> None:
        super().__init__(None)
        self.actors = actors

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        scene.create_actors(self.actors)
        world.create_renderers(self.actors)
        self.expire()


class DeleteActorsAnimation(Animation):
    def __init__(self, actor_ids: List[defs.ActorId]) -> None:
        super().__init__(None)
        self.actor_ids = actor_ids

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        scene.delete_actors(self.actor_ids)
        world.delete_renderers(self.actor_ids)
        self.expire()


class MovementAnimation(Animation):
    def __init__(
            self,
            actor_id: defs.ActorId,
            speed: float,
            bearing: float,
            timeout: float,
        ) -> None:
        super().__init__(timeout)
        self.actor_id = actor_id
        self.speed = speed
        self.bearing = bearing
        self._tick_count = 0

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        distance = self.speed * interval
        actor = scene.get_actor(self.actor_id)
        actor.move_by(distance, self.bearing, scene.get_radius())
        if self._tick_count == 0:
            world.play_animation(self.actor_id, AnimationName.WALK)
        self._tick_count += 1


class LocalizeAnimation(Animation):
    def __init__(self, actor_id: defs.ActorId, position: geometry.Point) -> None:
        super().__init__(None)
        self.actor_id = actor_id
        self.position = position

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        actor = scene.get_actor(self.actor_id)
        if actor is not None:
            actor.set_position(self.position)
        world.play_animation(self.actor_id, AnimationName.IDLE)
        self.expire()


class StatUpdateAnimation(Animation):
    def __init__(self, actor_id, stats: defs.Stats) -> None:
        super().__init__(None)
        self.actor_id = actor_id
        self.stats = stats

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        dials.set_stats(self.stats)
        self.expire()


class PickStartAnimation(Animation):
    def __init__(self, actor_id: defs.ActorId, item_id: defs.ActorId) -> None:
        super().__init__(None)
        self.actor_id = actor_id
        self.item_id = item_id

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        world.play_animation(self.actor_id, AnimationName.PICK)
        self.expire()


class PickEndAnimation(Animation):
    def __init__(self, actor_id: defs.ActorId) -> None:
        super().__init__(None)
        self.actor_id = actor_id

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        world.play_animation(self.actor_id, AnimationName.IDLE)
        self.expire()


class UpdateInventoryAnimation(Animation):
    def __init__(self, inventory: inventory.Inventory) -> None:
        super().__init__(None)
        self.inventory = inventory

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        dials.set_inventory(self.inventory)
        self.expire()


class DamageAnimation(Animation):
    def __init__(
            self,
            dealer_id: defs.ActorId,
            receiver_id: defs.ActorId,
            variant: defs.DamageVariant,
        ) -> None:
        super().__init__(None)
        self.dealer_id = dealer_id
        self.receiver_id = receiver_id
        self.variant = variant

    def tick(self, interval, scene: scene.Scene, world: world.World, dials: dials.Dials) -> None:
        # TODO: Implement animations and play damage animation here
        self.expire()

