import math

from typing import Iterable, List, Optional

from . import entity, geometry


class State:
    def __init__(self, elevation_function, entities: List[entity.Entity]) -> None:
        self.elevation_function = elevation_function
        self.entities = {e.get_id(): e for e in entities}

    def get_performers(self):
        return [e for e in self.entities.values() if e.features.performer is not None]

    def get_entities(self) -> Iterable[entity.Entity]:
        return self.entities.values()

    def get_entity(self, entity_id: int) -> Optional[entity.Entity]:
        return self.entities.get(entity_id, None)


class WorldGenerator:
    def generate_basic(self, radius) -> State:
        elevation_function = geometry.ElevationFunction(radius)
        entities: List[entity.Entity] = list()
        return State(elevation_function, entities)

    def generate(self, radius) -> State:
        # Elevation
        def hills(theta, phi) -> float:
            return 0.003 * radius \
                * (theta / math.pi - 1) * math.sin(50 * phi) \
                * (theta / math.pi - 2) * math.sin(50 * theta)

        def ranges(theta, phi) -> float:
            return 0.006 * radius * math.cos(10 * theta + math.pi) * math.cos(10 * phi)

        def continents(theta, phi) -> float:
            return 0.009 * radius * math.sin(theta) * math.sin(phi)

        elevation_function = geometry.ElevationFunction(radius)
        elevation_function.add(hills)
        elevation_function.add(ranges)
        elevation_function.add(continents)

        # Entities
        entities: List[entity.Entity] = [
            entity.Hero(0, (0.5 * math.pi, 0.0 * math.pi)),
            entity.Warior(1, (0.499 * math.pi, 0.001 * math.pi)),
            entity.Warior(2, (0.498 * math.pi, 0.002 * math.pi)),
        ]

        return State(elevation_function, entities)

