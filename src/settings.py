from typing import Any, Dict

from .craft import Ingredient, Material, Recipe

RECIPES = [
    Recipe(
        codename='axe',
        description='Axe',
        ingredients=[
            Ingredient(Material.MINERAL, 2),
            Ingredient(Material.WOOD, 1),
        ]
    ),
    Recipe(
        codename='hat',
        description='Hat',
        ingredients=[
            Ingredient(Material.LEATHER, 2),
            Ingredient(Material.ORNAMENT, 1),
            Ingredient(Material.GADGET, 1),
        ]
    ),
]

ENTITIES: Dict[str, Any] = dict()

