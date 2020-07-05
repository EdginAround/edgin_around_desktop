import math

from typing import Iterable, List, Optional

from . import entities, essentials, geometry


class State:
    def __init__(self, elevation_function, entities: List[essentials.Entity]) -> None:
        self.elevation_function = elevation_function
        self.entities = {e.get_id(): e for e in entities}

    def get_entities(self) -> Iterable[essentials.Entity]:
        return self.entities.values()

    def get_entity(self, entity_id: int) -> Optional[essentials.Entity]:
        return self.entities.get(entity_id, None)

    def get_distance(self, entity1: essentials.Entity, entity2: essentials.Entity) -> float:
        point1 = geometry.Point(*entity1.position)
        point2 = geometry.Point(*entity2.position)
        return point1.great_circle_distance_to(point2, self.elevation_function.get_radius())


class WorldGenerator:
    def generate_basic(self, radius) -> State:
        elevation_function = geometry.ElevationFunction(radius)
        entities: List[essentials.Entity] = list()
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
        entity_list: List[essentials.Entity] = [
            entities.Axe(4, (0.501 * math.pi, -0.001 * math.pi)),
            entities.Hero(0, (0.500 * math.pi, 0.000 * math.pi)),
            entities.Warior(1, (0.499 * math.pi, 0.001 * math.pi)),
            entities.Warior(2, (0.498 * math.pi, 0.002 * math.pi)),
            entities.Rocks(3, (0.497 * math.pi, 0.003 * math.pi)),
        ]

        return State(elevation_function, entity_list)

