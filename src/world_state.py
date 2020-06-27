import math

from typing import List

from . import entity, geometry


class WorldState:
    def __init__(self, elevation_function, entities: List[entity.Entity]) -> None:
        self.elevation_function = elevation_function
        self.entities = entities

    def get_performers(self):
        return [e for e in self.entities if e.features.performer is not None]


class WorldGenerator:
    def generate_basic(self, radius) -> WorldState:
        elevation_function = geometry.ElevationFunction(radius)
        entities: List[entity.Entity] = list()
        return WorldState(elevation_function, entities)

    def generate(self, radius) -> WorldState:
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
            entity.Warior(2, (0.499 * math.pi, 0.001 * math.pi)),
            entity.Warior(3, (0.498 * math.pi, 0.002 * math.pi)),
        ]

        return WorldState(elevation_function, entities)

