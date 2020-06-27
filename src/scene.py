from typing import Dict, Iterable, List, Optional

from . import geometry, graphics

ActorId = int


class Actor:
    def __init__(self, id, theta, phi, texture_name) -> None:
        self.id = id
        self.theta = theta
        self.phi = phi
        self.texture_name = texture_name

    def move_by(self, distance, bearing, radius) -> None:
        point = geometry.Point(self.theta, self.phi).moved_by(distance, bearing, radius)
        self.theta, self.phi = point.theta, point.phi

    def get_id(self):
        return self.id

class Scene:
    def __init__(self) -> None:
        self.elevation_function: Optional[geometry.ElevationFunction] = None
        self.actors: Dict[ActorId, Actor] = dict()

    def is_ready(self) -> bool:
        return self.elevation_function is not None

    def get_radius(self) -> float:
        if self.elevation_function:
            return self.elevation_function.get_radius()
        else:
            return 0.0

    def get_elevation(self, theta, phi, with_radius=False) -> float:
        if self.elevation_function is not None:
            if with_radius:
                return self.elevation_function.evaluate_with_radius(theta, phi)
            else:
                return self.elevation_function.evaluate_without_radius(theta, phi)
        else:
            return 0.0

    def get_actor(self, actor_id: ActorId) -> Actor:
        if actor_id in self.actors:
            return self.actors[actor_id]
        else:
            return Actor(-1, 0.0, 0.0, '')

    def get_actors(self) -> Iterable[Actor]:
        return self.actors.values()

    def configure(self, elevation_function):
        self.elevation_function = elevation_function

    def create_actors(self, actors: Iterable[Actor]) -> None:
        for actor in actors:
            self.actors[actor.id] = actor


