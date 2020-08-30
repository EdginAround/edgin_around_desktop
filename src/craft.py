# This file provides functionality related to crafting - recipes, items, item categories, etc.

from enum import unique, auto, Enum

from typing import Dict, Iterable, List, Optional, Set

from . import defs


@unique
class Essence(Enum):
    """Represents a general category of an item/entity."""

    # Raw materials
    ROCKS = 'rocks'
    GOLD = 'gold'
    LOGS = 'log'
    STICKS = 'sticks'

    # Clothing
    HAT = 'hat'
    COAT = 'coat'
    GLOVES = 'gloves'
    SHOES = 'shoes'
    BELT = 'belt'
    BOTTOM_WEAR = 'bottom_wear'
    UPPER_WEAR = 'upper_wear'
    BAG = 'bag'

    # Other
    PLANT = 'plant'
    HERO = 'hero'
    TOOL = 'tool'

    # Default category
    VOID = 'void'

    def get_description(self) -> str:
        """Returns a description of the essence to be used in GUI labels."""

        if self in _ESSENCE_DESCRIPTIONS:
            return _ESSENCE_DESCRIPTIONS[self]
        else:
            return '[Unknown]'

    def get_image_name(self) -> str:
        return self.value


_ESSENCE_DESCRIPTIONS: Dict[Essence, str] = {
    Essence.ROCKS: 'Rocks',
    Essence.GOLD: 'Gold',
    Essence.LOGS: 'Logs',
    Essence.STICKS: 'Sticks',
    Essence.HAT: 'Hat',
    Essence.COAT: 'Coat',
    Essence.GLOVES: 'Gloves',
    Essence.SHOES: 'Shoes',
    Essence.BELT: 'Belt',
    Essence.BOTTOM_WEAR: 'Bottom Wear',
    Essence.UPPER_WEAR: 'Upper Wear',
    Essence.BAG: 'Bag',
    Essence.PLANT: 'Plant',
    Essence.HERO: 'Hero',
    Essence.TOOL: 'Tool',
}


@unique
class Material(Enum):
    """Represents a category of a recipe ingredient. Only entities with `Essence` matching the
    `Material` can be used the given recipe ingredient."""

    FABRIC = 'fabric'
    GADGET = 'gadget'
    LEATHER = 'leather'
    MEAT = 'meat'
    MINERAL = 'mineral'
    ORNAMENT = 'ornament'
    WATER = 'water'
    WOOD = 'wood'

    def get_description(self) -> str:
        if self in _MATERIAL_DESCRIPTIONS:
            return _MATERIAL_DESCRIPTIONS[self]
        else:
            return '[Unknown]'


_MATERIAL_DESCRIPTIONS: Dict[Material, str] = {
    Material.FABRIC: 'Fabric',
    Material.GADGET: 'Gadget',
    Material.LEATHER: 'Leather',
    Material.MEAT: 'Meat',
    Material.MINERAL: 'Mineral',
    Material.ORNAMENT: 'Ornament',
    Material.WATER: 'Water',
    Material.WOOD: 'Wood',
}


class Match:
    """Matches `Material` with `Essence`."""

    def __init__(self, material: Material, essence: Essence) -> None:
        self.material = material
        self.essence = essence

    def __repr__(self) -> str:
        return f'Match({self.material.get_description()}, {self.essence.get_description()})'

    def __eq__(self, other) -> bool:
        return self.material == other.material and self.essence == other.essence

    def __hash__(self) -> int:
         return hash((self.material, self.essence))


_MATCHES = {
    Match(Material.MINERAL, Essence.ROCKS),
    Match(Material.MINERAL, Essence.GOLD),
    Match(Material.WOOD, Essence.LOGS),
}


class Item:
    """Represents an item that can be used as an ingredient in a recipe."""

    def __init__(self, actor_id: defs.ActorId, essence: Essence, quantity: int) -> None:
        self.actor_id = actor_id
        self.essence = essence
        self.quantity = quantity

    def __repr__(self) -> str:
        return f'Item(id={self.actor_id}, ' \
            f'essence={self.essence.get_description()}, quantity={self.quantity})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Item) \
           and self.actor_id == other.actor_id \
           and self.essence == other.essence \
           and self.quantity == other.quantity

    def __hash__(self) -> int:
         return hash((self.actor_id, self.essence, self.quantity))


class Ingredient:
    """Represents an ingredient in a recipe."""

    def __init__(self, material: Material, value: int, optional: bool = False) -> None:
        self.material = material
        self.value = value
        self.optional = optional

    def get_description(self) -> str:
        """Returns the description of the ingredients material."""

        return self.material.get_description()

    def match_essence(self, essence: Essence) -> bool:
        """Checks if an item with the given essence can be used as this recipe ingredient."""

        return Match(self.material, essence) in _MATCHES

    def filter_items(self, items: Iterable[Item]) -> Set[Item]:
        """Filters the passed iterable leaving only such items that can be used as this recipe
        ingredient."""

        result: Set[Item] = set()
        for item in items:
            if self.match_essence(item.essence):
                result.add(item)
        return result

    def __repr__(self) -> str:
        optional = 'optional' if self.optional else 'required'
        return f'Ingredient({self.material.get_description()}, {self.value}, {optional})'


class Assembly:
    """Represents a set of items that may be used in the corresponding recipe."""

    def __init__(self, recipe_codename: str, sources: List[List[Item]]) -> None:
        self.recipe_codename = recipe_codename
        self.sources = sources

    def find_item(self, actor_id: defs.ActorId, index: Optional[int]) -> Optional[Item]:
        """Checks if the entity with given ID is part of this assembly. If `index` is passes only
        items corresponding to the corresponding ingredient will be checked."""

        if index is not None and (index < 0 or len(self.sources) < index):
            return None

        all_sources = self.sources if index is None else [self.sources[index]]
        for ingredient_sources in all_sources:
            for item in ingredient_sources:
                if item.actor_id == actor_id:
                    return item
        return None

    def update_item(self, index: int, template: Item, change: int) -> bool:
        """
        Updates (adds, removes or changes quantity) an item in this assembly.
        Returns
         * True - if the operation is allowed and was performed correctly
         * False - if the operation is not allowed or failed
        """

        if index < 0 or len(self.sources) < index:
            return False

        item = self.find_item(template.actor_id, index)
        if item is not None:
            if (-1 * item.quantity) == change:
                self.sources[index].remove(item)
                return True
            elif (-1 * item.quantity) < change:
                item.quantity += change
                return True
            else:
                return False

        else:
            if 0 < change:
                self.sources[index].append(Item(template.actor_id, template.essence, change))
                return True
            else:
                return False

    def filter_items(self, items: Iterable[Item]) -> Set[Item]:
        """Given an iterable of `Item`s reduces their quantity (removing if needed) by quantity of
        corresponding entities contained in this assembly."""

        items = list(items)
        for sources in self.sources:
            for source in sources:
                for i in range(len(items)):
                    if items[i].actor_id == source.actor_id:
                        items[i].quantity -= source.quantity
                        break
        return set(filter(lambda e: e.quantity > 0, items))

    def __repr__(self) -> str:
        return f'Assembly({self.recipe_codename}, {self.sources})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Assembly) \
           and self.recipe_codename == other.recipe_codename \
           and [set(src) for src in self.sources] == [set(src) for src in other.sources]


class Recipe:
    """Represents a recipe to craft items in the game."""

    def __init__(self, codename: str, description: str, ingredients: List[Ingredient]) -> None:
        self._codename = codename
        self._description = description
        self._ingredients = ingredients

    def get_codename(self) -> str:
        return self._codename

    def get_description(self) -> str:
        return self._description

    def get_ingredients(self) -> List[Ingredient]:
        return list(self._ingredients)

    def make_assembly(self) -> Assembly:
        """Returns and empty `Assembly` corresponding to this recipe."""

        return Assembly(self._codename, [list() for _ in self._ingredients])

    def validate_assembly(self, assembly: Assembly) -> bool:
        """"Checks if the passed `Assembly` satisfies the recipes requirements."""

        if len(self.get_ingredients()) != len(assembly.sources):
            return False

        for ingredient, sources in zip(self.get_ingredients(), assembly.sources):
            for source in sources:
                if not ingredient.match_essence(source.essence):
                    return False

            total_quantity = sum(source.quantity for source in sources)
            if total_quantity != ingredient.value:
                return False

        return True

