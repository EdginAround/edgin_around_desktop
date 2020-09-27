import math

from typing import List

from . import entities, essentials, geometry, state


class WorldGenerator:
    def generate_basic(self, radius) -> state.State:
        elevation_function = geometry.ElevationFunction(radius)
        entities: List[essentials.Entity] = list()
        return state.State(elevation_function, entities)

    def generate(self, radius) -> state.State:
        # Elevation
        def hills(pos: geometry.Point) -> float:
            return 0.003 * radius \
                * (pos.theta / math.pi - 1) * math.sin(50 * pos.phi) \
                * (pos.theta / math.pi - 2) * math.sin(50 * pos.theta)

        def ranges(pos: geometry.Point) -> float:
            return 0.006 * radius * math.cos(10 * pos.theta + math.pi) * math.cos(10 * pos.phi)

        def continents(pos: geometry.Point) -> float:
            return 0.009 * radius * math.sin(pos.theta) * math.sin(pos.phi)

        elevation_function = geometry.ElevationFunction(radius)
        elevation_function.add(hills)
        elevation_function.add(ranges)
        elevation_function.add(continents)

        # Entities
        entity_list: List[essentials.Entity] = [
            entities.Pirate(0, (0.500 * math.pi, 0.000 * math.pi)),
            entities.Axe(1, (0.501 * math.pi, -0.001 * math.pi)),
            entities.Warrior(2, (0.499 * math.pi, 0.001 * math.pi)),
            entities.Warrior(3, (0.498 * math.pi, 0.002 * math.pi)),
            entities.Rocks(4, (0.497 * math.pi, 0.003 * math.pi)),
            entities.Rocks(5, (0.495 * math.pi, 0.005 * math.pi)),
            entities.Gold(6, (0.496 * math.pi, 0.004 * math.pi)),
            entities.Spruce(7, (0.493 * math.pi, -0.003 * math.pi)),
        ]

        return state.State(elevation_function, entity_list)

