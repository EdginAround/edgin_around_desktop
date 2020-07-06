from typing import Iterable, List, Optional

from . import essentials, geometry


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

    def get_distance(
            self,
            entity1: essentials.Entity,
            entity2: essentials.Entity,
            ) -> Optional[float]:
        if entity1.position is not None and entity2.position is not None:
            radius = self.elevation_function.get_radius()
            return entity1.position.great_circle_distance_to(entity2.position, radius)
        else:
            return None

