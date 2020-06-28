import time

from typing import Iterable, List, Optional

from . import scene


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
    def get_actor_id(self) -> Optional[scene.ActorId]:
        return None

    def expire(self) -> None:
        self._expired = True

    def tick(self, tick_interval, scene: scene.Scene) -> None:
        raise NotImplementedError('This animation is not implemented')


class ConfigurationAnimation(Animation):
    def __init__(self, hero_actor_id: int, elevation_function) -> None:
        super().__init__(None)
        self.hero_actor_id = hero_actor_id
        self.elevation_function = elevation_function

    def tick(self, tick_interval, scene: scene.Scene) -> None:
        scene.configure(self.hero_actor_id, self.elevation_function)
        self.expire()


class CreateActorsAnimation(Animation):
    def __init__(self, actors: List[scene.Actor]) -> None:
        super().__init__(None)
        self.actors = actors

    def tick(self, tick_interval, scene: scene.Scene) -> None:
        scene.create_actors(self.actors)
        self.expire()


class MovementAnimation(Animation):
    def __init__(self, timeout, actor_id: scene.ActorId, bearing, speed) -> None:
        super().__init__(timeout)
        self.actor_id = actor_id
        self.bearing = bearing
        self.speed = speed

    def get_actor_id(self) -> scene.ActorId:
        return self.actor_id

    def tick(self, tick_interval, scene: scene.Scene) -> None:
        distance = self.speed * tick_interval
        actor = scene.get_actor(self.actor_id)
        actor.move_by(distance, self.bearing, scene.get_radius())


class LocalizeAnimation(Animation):
    def __init__(self, actor_id: scene.ActorId) -> None:
        super().__init__(None)
        self.actor_id = actor_id

    def get_actor_id(self) -> scene.ActorId:
        return self.actor_id

    def tick(self, tick_interval, scene: scene.Scene) -> None:
        self.expire()

