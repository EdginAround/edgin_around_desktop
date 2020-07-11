import random

from typing import Iterable, List, Optional

from . import defs, essentials, features, geometry


class State:
    def __init__(
            self,
            elevation_function: geometry.ElevationFunction,
            entities: List[essentials.Entity],
        ) -> None:
        self.elevation_function = elevation_function
        self.entities = {e.get_id(): e for e in entities}

    def get_entities(self) -> Iterable[essentials.Entity]:
        return self.entities.values()

    def get_entity(self, entity_id: int) -> Optional[essentials.Entity]:
        return self.entities.get(entity_id, None)

    def get_radius(self) -> float:
        return self.elevation_function.get_radius()

    def calculate_distance(
            self,
            entity1: essentials.Entity,
            entity2: essentials.Entity,
            ) -> Optional[float]:
        if entity1.position is not None and entity2.position is not None:
            radius = self.elevation_function.get_radius()
            return entity1.position.great_circle_distance_to(entity2.position, radius)
        else:
            return None

    def find_closest_delivering_within(
            self,
            reference_id: defs.ActorId,
            claim: Iterable[features.Claim],
            max_distance: float,
        ) -> Optional[defs.ActorId]:
        reference = self.get_entity(reference_id)
        if reference is None:
            return None

        min_id = None
        min_distance = 100 * self.get_radius()
        for entity in self.entities.values():
            if entity.get_id() != reference_id and entity.features.deliver(claim):
                distance = self.calculate_distance(reference, entity)
                if distance is not None and distance < min_distance:
                    min_distance = distance
                    min_id = entity.get_id()

        return min_id

    def find_closest_absorbing_within(
            self,
            reference_id: defs.ActorId,
            claims: Iterable[features.Claim],
            max_distance: float,
        ) -> Optional[defs.ActorId]:
        reference = self.get_entity(reference_id)
        if reference is None:
            return None

        min_id = None
        min_distance = 100 * self.get_radius()
        for entity in self.entities.values():
            if entity.get_id() != reference_id and entity.features.absorb(claims):
                distance = self.calculate_distance(reference, entity)
                if distance is not None and distance < min_distance:
                    min_distance = distance
                    min_id = entity.get_id()

        return min_id

    def add_entity(self, entity: essentials.Entity) -> None:
        id = entity.get_id()
        while id in self.entities:
            id = random.randint(0, 1000000)
        entity.id = id
        self.entities[id] = entity

