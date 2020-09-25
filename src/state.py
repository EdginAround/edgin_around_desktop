import random, sys

from typing import Iterable, List, Optional

from . import craft, defs, essentials, features, inventory, geometry, scene, settings

class CraftResult:
    def __init__(
            self,
            created: List[scene.Actor] = list(),
            deleted: List[defs.ActorId] = list(),
        ) -> None:
        self.created = created
        self.deleted = deleted

    def add_for_creation(self, created: scene.Actor) -> None:
        self.created.append(created)

    def add_for_deletion(self, deleted: defs.ActorId) -> None:
        self.deleted.append(deleted)


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
        while id in self.entities or id < 0:
            id = random.randint(0, 1000000)
        entity.id = id
        self.entities[id] = entity

    def delete_entity(self, entity_id: defs.ActorId) -> None:
        del self.entities[entity_id]

    def validate_assembly(self, assembly: craft.Assembly, inventory: inventory.Inventory) -> bool:
        recipe = self._find_recipe_by_codename(assembly.recipe_codename)
        if recipe is None:
            return False

        if not recipe.validate_assembly(assembly):
            return False

        for ingredient, sources in zip(recipe.get_ingredients(), assembly.sources):
            for source in sources:
                entry = inventory.find_entity_with_entity_id(source.actor_id)
                if entry is None:
                    return False

                entity = self.get_entity(entry.id)
                if entity is None:
                    return False

                if not ingredient.match_essence(entity.ESSENCE):
                    return False

                if entity.features.stackable is not None:
                    if entity.features.stackable.get_size() < source.quantity:
                        return False
                else:
                    if source.quantity > 1:
                        return False

        return True

    def craft_entity(self, assembly: craft.Assembly, inventory: inventory.Inventory) -> CraftResult:
        if self.validate_assembly(assembly, inventory):
            return self._craft(assembly, inventory)
        else:
            return CraftResult()

    def _craft(self, assembly: craft.Assembly, inventory: inventory.Inventory) -> CraftResult:
        result = CraftResult()
        recipe = self._find_recipe_by_codename(assembly.recipe_codename)
        assert recipe is not None

        free_hand = inventory.get_free_hand()
        if free_hand is None:
            return result

        # Crafting new entity
        new_entity = self._construct_entity(
                recipe.get_codename(),
                self._prepare_new_entity_id(),
                None,
            )
        if new_entity is None:
            return result

        # Deleting ingredients
        for sources in assembly.sources:
            for source in sources:
                entry = inventory.find_entity_with_entity_id(source.actor_id)
                assert entry is not None
                entity = self.get_entity(entry.id)
                assert entity is not None

                if entity.features.stackable is not None:
                    if entity.features.stackable.get_size() == source.quantity:
                        inventory.remove_with_entity_id(entity.id)
                        result.add_for_deletion(entity.id)
                        self.delete_entity(entity.id)
                    else:
                        entity.features.stackable.decrease(source.quantity)
                else:
                    inventory.remove_with_entity_id(entity.id)
                    result.add_for_deletion(entity.id)
                    self.delete_entity(entity.id)

        # Add the new entity
        inventory.store(
                free_hand,
                new_entity.get_id(),
                new_entity.get_essence(),
                1,
                new_entity.get_name(),
            )

        self.add_entity(new_entity)
        result.add_for_creation(new_entity.as_actor())
        return result

    def _find_recipe_by_codename(self, codename: str) -> Optional[craft.Recipe]:
        for recipe in settings.RECIPES:
            if recipe.get_codename() == codename:
                return recipe
        return None

    def _prepare_new_entity_id(self) -> defs.ActorId:
        while True:
            id = defs.ActorId(random.randint(0, sys.maxsize))
            if id not in self.entities:
                return id

    def _construct_entity(
            self,
            codename: str,
            id: defs.ActorId,
            position: essentials.EntityPosition,
        ) -> Optional[essentials.Entity]:
        if codename in settings.ENTITIES:
            return settings.ENTITIES[codename](id, position)
        else:
            return None

