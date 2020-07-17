from typing import Dict, Iterable, List, Optional, Tuple

from . import defs, geometry, graphics


class Actor:
    def __init__(
            self,
            id: defs.ActorId,
            position: Optional[geometry.Point],
            entity_name: str,
        ) -> None:
        self.id = id
        self.position = position
        self.entity_name = entity_name

    def get_id(self) -> defs.ActorId:
        return self.id

    def set_position(self, position: geometry.Point) -> None:
        self.position = position

    def move_by(self, distance, bearing, radius) -> None:
        if self.position is not None:
            self.position = self.position.moved_by(distance, bearing, radius)


class Scene:
    def __init__(self) -> None:
        self.elevation_function: Optional[geometry.ElevationFunction] = None
        self.actors: Dict[defs.ActorId, Actor] = dict()

    def is_ready(self) -> bool:
        return self.elevation_function is not None

    def get_radius(self) -> float:
        if self.elevation_function:
            return self.elevation_function.get_radius()
        else:
            return 0.0

    def get_elevation(self, position: geometry.Point, with_radius=False) -> float:
        if self.elevation_function is not None:
            if with_radius:
                return self.elevation_function.evaluate_with_radius(position)
            else:
                return self.elevation_function.evaluate_without_radius(position)
        else:
            return 0.0

    def get_actor(self, actor_id: defs.ActorId) -> Actor:
        if actor_id in self.actors:
            return self.actors[actor_id]
        else:
            return Actor(-1, geometry.Point(0.0, 0.0), '')

    def get_actors(self) -> Iterable[Actor]:
        return self.actors.values()

    def get_hero_position(self) -> geometry.Point:
        hero = self.actors[self.hero_actor_id]
        assert hero.position is not None
        return hero.position

    def configure(self, hero_actor_id, elevation_function):
        self.hero_actor_id = hero_actor_id
        self.elevation_function = elevation_function

    def create_actors(self, actors: Iterable[Actor]) -> None:
        for actor in actors:
            self.actors[actor.id] = actor

    def delete_actors(self, actor_ids: Iterable[defs.ActorId]) -> None:
        for id in actor_ids:
            if id in self.actors:
                del self.actors[id]


