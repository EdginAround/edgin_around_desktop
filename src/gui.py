#!/usr/bin/env python

import enum, math

import pyglet

from typing import cast, List, Optional, Union

from . import formations, formations_images, formations_renderer
from . import craft, defs, graphics, inventory, media, proxy, settings, world


_INVENTORY_IMAGE_SIZE = formations.Size(100, 100)


class WorldFormation(formations.Formation):
    def __init__(self, world: world.World, proxy: proxy.Proxy) -> None:
        super().__init__()
        self._world = world
        self._proxy = proxy
        self._fbo = graphics.Fbo()
        self._flip_vertical = True

    def resize(self, size: formations.Size) -> bool:
        if super().resize(size):
            size = self.get_size()
            width, height = int(size.width), int(size.height)

            self._fbo.resize(width, height)
            self._world.resize(width, height)

            content = formations.Content(size, self._fbo.get_color_texture_id())
            self.set_content(content)

            return True

        else:
            return False

    def draw(self) -> None:
        with self._fbo:
            self._world.draw()

    def on_grab(self, position: formations.Position, *args) -> formations.EventResult:
        button, modifiers = args
        if button == pyglet.window.mouse.LEFT:
            if id := self._world.get_highlight_actor_id():
                self._proxy.send_hand(defs.Hand.LEFT, id)
        elif button == pyglet.window.mouse.RIGHT:
            if id := self._world.get_highlight_actor_id():
                self._proxy.send_hand(defs.Hand.RIGHT, id)
        return formations.EventResult.HANDLED

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        button, modifiers = args
        if button in (pyglet.window.mouse.LEFT, pyglet.window.mouse.RIGHT):
            self._proxy.send_conclude()
        return formations.EventResult.HANDLED


class MapFormation(formations.Formation):
    def __init__(self) -> None:
        super().__init__()

        content = formations_images.ImageFileContent('res/images/map.png')
        self.set_content(content)


class InventoryLabel(formations_images.Label):
    MARGIN = 0
    PADDING = 0
    BG_COLOR = formations.Color(0.0, 0.0, 0.0, 0.0)
    FG_COLOR = formations.Color(0.0, 0.0, 0.0, 1.0)
    FONT_SIZE = 16
    FONT = "DejaVuSans-Bold.ttf"

    def __init__(self, text: str, gravity: formations.Gravity) -> None:
        super().__init__(
            text=text,
            gravity=gravity,
            margin=self.MARGIN,
            padding=self.PADDING,
            bg_color=self.BG_COLOR,
            fg_color=self.FG_COLOR,
            font_size=self.FONT_SIZE,
        )


class HandFormation(formations.Formation):
    def __init__(self) -> None:
        super().__init__()

    def set_image(self, texture_id: int) -> None:
        content = formations.Content(_INVENTORY_IMAGE_SIZE, texture_id)
        self.set_content(content)


class PocketFormation(formations.Clasp):
    def __init__(self, index: int, proxy: proxy.Proxy) -> None:
        from .formations import Expanse, Gravity, Orientation

        super().__init__()
        self._index = index
        self._proxy = proxy

        self._id_label = InventoryLabel(str(index + 1), formations.Gravity.START)
        self._volume_label = InventoryLabel('', formations.Gravity.END)

        id_constraint = self.Constraint(
                orientation=Orientation.VERTICAL,
                stretch=1.0,
                expanse=Expanse.FIT,
                horizontal_gravity=Gravity.START,
                vertical_gravity=Gravity.END,
            )
        volume_constraint = self.Constraint(
                orientation=Orientation.VERTICAL,
                stretch=1.0,
                expanse=Expanse.FIT,
                horizontal_gravity=Gravity.END,
                vertical_gravity=Gravity.START,
            )

        self.add(self._id_label, id_constraint)
        self.add(self._volume_label, volume_constraint)

    def set_image_and_volume(self, texture_id: int, quantity_label: str) -> None:
        content = formations.Content(_INVENTORY_IMAGE_SIZE, texture_id)
        self.set_content(content)
        self._volume_label.set_text(quantity_label)

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        button, modifiers = args

        if button == pyglet.window.mouse.LEFT:
            self._proxy.send_inventory_merge(defs.Hand.LEFT, self._index)
        elif button == pyglet.window.mouse.RIGHT:
            self._proxy.send_inventory_merge(defs.Hand.RIGHT, self._index)

        return formations.EventResult.HANDLED


class PocketsFormation(formations.Grid):
    ROWS = 2
    COLUMS = 10

    def __init__(self, proxy: proxy.Proxy) -> None:
        super().__init__(self.ROWS, self.COLUMS)

        self.pockets = [
            [PocketFormation(i + j * self.COLUMS, proxy) for i in range(self.COLUMS)]
            for j in range(self.ROWS)
        ]
        for i, row in enumerate(self.pockets):
            for j, pocket in enumerate(row):
                self.insert(pocket, i, j)

    def get_pocket(self, index: int) -> PocketFormation:
        return cast(PocketFormation, self.get(index))


class InventoryFormation(formations.Stripe):
    LEFT_HAND = 'left_hand'
    RIGHT_HAND = 'right_hand'
    EMPTY_SLOT = 'empty_slot'

    def __init__(self, tex: media.Textures, proxy: proxy.Proxy) -> None:
        super().__init__(formations.Orientation.HORIZONTAL)

        self.left_hand = HandFormation()
        self.pockets = PocketsFormation(proxy)
        self.right_hand = HandFormation()

        self.left_hand.set_image(tex[self.LEFT_HAND])
        self.right_hand.set_image(tex[self.RIGHT_HAND])

        self.append(self.left_hand)
        self.append(self.pockets)
        self.append(self.right_hand)

    def set_inventory(self, inventory: inventory.Inventory, tex: media.Textures) -> None:
        img = inventory.left_hand.codename if inventory.left_hand is not None else self.LEFT_HAND
        self.left_hand.set_image(tex[img])

        img = inventory.right_hand.codename if inventory.right_hand is not None else self.RIGHT_HAND
        self.right_hand.set_image(tex[img])

        for i, entry in enumerate(inventory.entries):
            img, quantity_label = self.EMPTY_SLOT, ''
            if entry is not None:
                img, quantity_label = \
                    entry.codename, f'{entry.current_quantity}/{entry.max_quantity}'
            self.pockets.get_pocket(i).set_image_and_volume(tex[img], quantity_label)

        self.pockets.mark_as_needs_reallocation()


class StatFormation(formations_images.Label):
    MARGIN = 5
    PADDING = 5
    BG_COLOR = formations.Color(0.0, 0.5, 0.7, 1.0)
    FG_COLOR = formations.Color(1.0, 1.0, 1.0, 1.0)
    FONT_SIZE = 16

    def __init__(self, text: str) -> None:
        super().__init__(
            text=text,
            margin=self.MARGIN,
            padding=self.PADDING,
            bg_color=self.BG_COLOR,
            fg_color=self.FG_COLOR,
            font_size=self.FONT_SIZE,
        )


class StatsFormation(formations.Lineup):
    MARGIN = 5
    NONE = '--//--'

    def __init__(self) -> None:
        super().__init__(formations.Orientation.VERTICAL)

        self.hunger = StatFormation(self._format_hunger(self.NONE))

        self.append(self.hunger, self.Pack(1.0))

    def _format_hunger(self, value: Union[float, str]) -> str:
        return f'Hunger: {value}'

    def set_stats(self, stats: defs.Stats) -> None:
        self.hunger.set_text(self._format_hunger(stats.hunger))


class MainFormation(formations.Clasp):
    def __init__(self, tex: media.Textures, proxy: proxy.Proxy) -> None:
        from .formations import Expanse, Gravity, Orientation

        super().__init__()

        self._map_formation = MapFormation()
        self._stats_formation = StatsFormation()
        self._inventory_formation = InventoryFormation(tex, proxy)

        map_constraint = self.Constraint(
                orientation=Orientation.VERTICAL,
                stretch=0.2,
                expanse=Expanse.FIT,
                horizontal_gravity=Gravity.START,
                vertical_gravity=Gravity.END,
            )
        stats_constraint = self.Constraint(
                orientation=Orientation.VERTICAL,
                stretch=0.2,
                expanse=Expanse.FIT,
                horizontal_gravity=Gravity.END,
                vertical_gravity=Gravity.END,
            )
        inventory_constraint = self.Constraint(
                orientation=Orientation.HORIZONTAL,
                stretch=0.1,
                expanse=Expanse.FILL,
                horizontal_gravity=Gravity.CENTER,
                vertical_gravity=Gravity.START,
            )

        self.add(self._map_formation, map_constraint)
        self.add(self._stats_formation, stats_constraint)
        self.add(self._inventory_formation, inventory_constraint)

    def set_stats(self, stats: defs.Stats) -> None:
        self._stats_formation.set_stats(stats)

    def set_inventory(self, inventory: inventory.Inventory, tex: media.Textures) -> None:
        self._inventory_formation.set_inventory(inventory, tex)


class CraftLabel(formations_images.Label):
    MARGIN = 0
    PADDING = 5
    BG_COLOR = formations.Color(0.0, 0.0, 0.0, 0.0)
    FG_COLOR = formations.Color(1.0, 1.0, 1.0, 1.0)

    class Size(enum.IntEnum):
        BIG = 30
        NORMAL = 20
        SMALL = 10

    def __init__(self, size: Size, text='', gravity=formations.Gravity.CENTER) -> None:
        super().__init__(
            text=text,
            font_size=size,
            margin=self.MARGIN,
            padding=self.PADDING,
            fg_color=self.FG_COLOR,
            bg_color=self.BG_COLOR,
            gravity=gravity,
        )


class CraftButton(CraftLabel):
    ENABLED_BG_COLOR = formations.Color(0.1, 0.1, 0.5, 1.0)
    DISABLED_BG_COLOR = formations.Color(0.2, 0.2, 0.2, 1.0)

    def __init__(
            self,
            space: 'CraftingSpaceFormation',
            size: 'CraftButton.Size',
            text='',
            enabled=True,
        ) -> None:
        super().__init__(size, text, formations.Gravity.CENTER)
        self._space = space
        self._is_enabled = not enabled
        self.set_enabled(enabled)

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        if self._is_enabled:
            button, modifiers = args
            if button == pyglet.window.mouse.LEFT:
                self._space.craft_entity()
            return formations.EventResult.HANDLED
        else:
            return formations.EventResult.NOT_HANDLED

    def set_enabled(self, is_enabled: bool) -> None:
        if self._is_enabled != is_enabled:
            self.set_bg_color(self.ENABLED_BG_COLOR if is_enabled else self.DISABLED_BG_COLOR)
            self._is_enabled = is_enabled


class CraftItemFormation(formations.Lineup):
    def __init__(
            self,
            item: craft.Item,
            space: 'CraftingSpaceFormation',
            data: Optional[int],
        ) -> None:
        super().__init__(formations.Orientation.HORIZONTAL)
        self._item = item
        self._space = space
        self._data = data

        self._image = formations_images.ImageFormation(
                _INVENTORY_IMAGE_SIZE,
                space._tex[item.essence.get_image_name()],
            )

        self._label = CraftLabel(
                size=CraftLabel.Size.NORMAL,
                text=self._format_text(),
                gravity=formations.Gravity.START,
            )

        self.append(self._image, self.Pack(0))
        self.append(self._label, self.Pack(1))

    def calc_pref_height(self, width: float) -> float:
        return 2 * math.sqrt(width)

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        button, modifiers = args
        if button == pyglet.window.mouse.LEFT:
            self._space.update_item(self._item, self._data)
        return formations.EventResult.HANDLED

    def _format_text(self) -> str:
        return f'{self._item.quantity} × {self._item.essence.get_description()}'


class CraftIngredientFormation(formations.Stripe):
    ACTIVE_COLOR = formations.Color(5.0, 1.0, 5.0, 0.01)

    def __init__(
            self,
            ingredient: craft.Ingredient,
            index: int,
            space: 'CraftingSpaceFormation',
        ) -> None:
        super().__init__(formations.Orientation.VERTICAL)
        self._ingredient = ingredient
        self._index = index
        self._space = space

        self._is_active = False

        self._title = CraftLabel(size=CraftLabel.Size.NORMAL, text=ingredient.get_description())
        self._items = formations.Lineup(formations.Orientation.VERTICAL)
        self._comment = CraftLabel(size=CraftLabel.Size.NORMAL, text='')

        self.append(self._comment)
        self.append(self._items)
        self.append(self._title)

    def is_active(self) -> bool:
        return self._is_active

    def set_active(self, active: bool) -> None:
        self._is_active = active
        if active:
            content = formations.Content(_INVENTORY_IMAGE_SIZE, color=self.ACTIVE_COLOR)
            self.set_content(content)
        else:
            self.set_content(None)

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        if super().on_release(position, *args) == formations.EventResult.HANDLED:
            return formations.EventResult.HANDLED

        button, modifiers = args
        if button == pyglet.window.mouse.LEFT:
            if not self._is_active:
                self._space.change_active_ingredient(self._ingredient, self._index)
        return formations.EventResult.HANDLED

    def update_items(self, items: List[craft.Item]) -> None:
        self._items.clear()
        for item in items:
            item_formation = CraftItemFormation(item, self._space, data=self._index)
            self._items.append(item_formation, formations.Lineup.Pack(1))

        total_quantity = sum(item.quantity for item in items)
        self._comment.set_text(f'{total_quantity} / {self._ingredient.value}')


class CraftingRecipeFormation(formations.Lineup):
    def __init__(self) -> None:
        super().__init__(formations.Orientation.HORIZONTAL)
        self._active_ingredient_index = 0

    def get_active_ingredient_index(self) -> int:
        return self._active_ingredient_index

    def clear_with_recipe(self, recipe: craft.Recipe, space: 'CraftingSpaceFormation') -> None:
        self.clear()
        for index, ingredient in enumerate(recipe.get_ingredients()):
            ingredient_formation = CraftIngredientFormation(ingredient, index, space)
            ingredient_formation.set_active(index == 0)
            self.append(ingredient_formation, self.Pack(1))

    def update_ingredient(self, index: int, sources: List[craft.Item]) -> None:
        ingredient_formation = cast(CraftIngredientFormation, self._children[index])
        ingredient_formation.update_items(sources)

    def activate_ingredient(self, index: int) -> None:
        if index != self._active_ingredient_index:
            old = cast(CraftIngredientFormation, self._children[self._active_ingredient_index])
            new = cast(CraftIngredientFormation, self._children[index])
            old.set_active(False)
            new.set_active(True)
            self._active_ingredient_index = index

    def clear(self) -> None:
        super().clear()
        self._active_ingredient_index = 0


class CraftingSpaceFormation(formations.Lineup):
    def __init__(
            self,
            inventory: inventory.Inventory,
            tex: media.Textures,
            proxy: proxy.Proxy,
            gui: 'Gui',
        ) -> None:
        super().__init__(formations.Orientation.VERTICAL)
        self._inventory = inventory
        self._tex = tex
        self._proxy = proxy
        self._gui = gui

        self._recipe: Optional[craft.Recipe] = None
        self._assembly: Optional[craft.Assembly] = None

        self._title_formation = CraftLabel(size=CraftLabel.Size.BIG)
        self._button_formation = CraftButton(self, size=CraftButton.Size.BIG, enabled=False)
        self._header_formation = formations.Lineup(formations.Orientation.HORIZONTAL)
        self._recipe_formation = CraftingRecipeFormation()
        self._ingredients_formation = formations.Lineup(formations.Orientation.HORIZONTAL)
        self._inventory_formation = formations.Scroll(
                formations.Orientation.VERTICAL,
                formations.Gravity.END,
            )
        self._stock_formation = formations.Scroll(
                formations.Orientation.VERTICAL,
                formations.Gravity.END,
            )

        self._button_formation.set_text('Craft')

        self._ingredients_formation.append(self._inventory_formation, self.Pack(1))
        self._ingredients_formation.append(self._stock_formation, self.Pack(1))

        self._header_formation.append(self._title_formation, self.Pack(1))
        self._header_formation.append(self._button_formation, self.Pack(0))

        self.append(self._ingredients_formation, self.Pack(3))
        self.append(self._recipe_formation, self.Pack(2))
        self.append(self._header_formation, self.Pack(0))

    def change_recipe(self, recipe: craft.Recipe):
        self._recipe = recipe
        self._assembly = recipe.make_assembly()

        self._title_formation.set_text(recipe.get_description())
        self._recipe_formation.clear()
        self._inventory_formation.clear()
        self._stock_formation.clear()

        self._change_ingredients(recipe)
        self._change_items(recipe.get_ingredients()[0])

        self.mark_as_needs_update()

    def change_active_ingredient(self, ingredient: craft.Ingredient, index: int) -> None:
        self._recipe_formation.activate_ingredient(index)
        self._change_items(ingredient)

    def update_item(self, item: craft.Item, data: Optional[int]) -> None:
        assert self._assembly is not None and self._recipe is not None

        if data is not None:
            index, amount = data, -1
        else:
            index, amount = self._recipe_formation.get_active_ingredient_index(), 1

        if self._assembly.update_item(index, item, amount):
            self._recipe_formation.update_ingredient(index, self._assembly.sources[index])
            self._change_items(self._recipe.get_ingredients()[index])

        assembly_valid = self._recipe.validate_assembly(self._assembly)
        self._button_formation.set_enabled(assembly_valid)

    def craft_entity(self) -> None:
        assert self._assembly is not None
        self._proxy.send_craft(self._assembly)
        self.clear()
        self._gui.toggle_crafting()

    def _change_ingredients(self, recipe: craft.Recipe) -> None:
        self._recipe_formation.clear_with_recipe(recipe, self)

    def _change_items(self, ingredient: craft.Ingredient) -> None:
        assert self._assembly is not None

        self._inventory_formation.clear()
        items = self._inventory.to_items()
        items = ingredient.filter_items(items)
        items = self._assembly.filter_items(items)
        for i, item in enumerate(items):
            item_formation = CraftItemFormation(item, self, data=None)
            self._inventory_formation.append(item_formation)

    def set_inventory(self, inventory: inventory.Inventory) -> None:
        self._inventory = inventory

    def clear(self) -> None:
        self._recipe = None
        self._assembly = None
        self._title_formation.set_text('')
        self._button_formation.set_enabled(False)
        self._recipe_formation.clear()
        self._inventory_formation.clear()
        self._stock_formation.clear()


class RecipeTabFormation(formations.Formation):
    def __init__(
            self,
            space: CraftingSpaceFormation,
            recipe: craft.Recipe,
            tex: media.Textures,
        ) -> None:
        super().__init__()
        self._recipe = recipe
        self._space = space

        content = formations.Content(_INVENTORY_IMAGE_SIZE, tex[recipe.get_codename()])
        self.set_content(content)

    def on_grab(self, position: formations.Position, *args) -> formations.EventResult:
        return formations.EventResult.HANDLED

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        self._space.change_recipe(self._recipe)
        return formations.EventResult.HANDLED


class CraftingFormation(formations.Lineup):
    BG_COLOR = formations.Color(0.1, 0.1, 0.1, 0.9)

    def __init__(
            self,
            inventory: inventory.Inventory,
            tex: media.Textures,
            proxy: proxy.Proxy,
            gui: 'Gui',
        ) -> None:
        super().__init__(formations.Orientation.HORIZONTAL)

        self.recipe_tabs = formations.Scroll(
                formations.Orientation.VERTICAL,
                formations.Gravity.END,
            )
        self.crafting_space = CraftingSpaceFormation(inventory, tex, proxy, gui)

        self.append(self.recipe_tabs, self.Pack(1.0))
        self.append(self.crafting_space, self.Pack(9.0))

        for recipe in settings.RECIPES[::-1]:
            button = RecipeTabFormation(self.crafting_space, recipe, tex)
            self.recipe_tabs.append(button)

        content = formations.Content(_INVENTORY_IMAGE_SIZE, color=self.BG_COLOR)
        self.set_content(content)

    def on_grab(self, position: formations.Position, *args) -> formations.EventResult:
        super().on_grab(position, *args)
        return formations.EventResult.HANDLED

    def on_release(self, position: formations.Position, *args) -> formations.EventResult:
        super().on_release(position, *args)
        return formations.EventResult.HANDLED

    def set_inventory(self, inventory: inventory.Inventory) -> None:
        self.crafting_space.set_inventory(inventory)


class Gui(formations.Stack):
    def __init__(self, world: world.World, proxy: proxy.Proxy) -> None:
        super().__init__()

        self._world = world
        self._formation_group = formations_renderer.FormationGroup()
        self._inventory = inventory.Inventory()

        self._media = media.Media()
        self._media.load_inventory()

        self._world_formation = WorldFormation(world, proxy)
        self._main_formation = MainFormation(self._media.tex, proxy)
        self._crafting_formation = CraftingFormation(self._inventory, self._media.tex, proxy, self)

        self._crafting_formation.set_is_visible(False)

        self.add(self._world_formation)
        self.add(self._main_formation)
        self.add(self._crafting_formation)

    def set_stats(self, stats: defs.Stats) -> None:
        self._main_formation.set_stats(stats)

    def set_inventory(self, inventory: inventory.Inventory) -> None:
        self._inventory = inventory
        self._main_formation.set_inventory(inventory, self._media.tex)
        self._crafting_formation.set_inventory(inventory)

    def toggle_crafting(self) -> None:
        self._main_formation.set_is_visible(not self._main_formation.get_is_visible())
        self._crafting_formation.set_is_visible(not self._crafting_formation.get_is_visible())

    def handle_resize(self, width: float, height: float) -> None:
        self.resize(formations.Size(width, height))
        self._formation_group.resize(width, height)

    def handle_button_press(self, x, y, button, modifiers) -> None:
        self.on_grab(formations.Position(x, y), button, modifiers)

    def handle_button_release(self, x, y, button, modifiers) -> None:
        self.on_release(formations.Position(x, y), button, modifiers)

    def handle_mouse_motion(self, x: float, y: float) -> None:
        # TODO: All mouse motion events are passed to `world` now. Pass them to all formations
        # and implement `enter` and `leave` events.
        self._world.highlight(x, y)

    def draw(self) -> None:
        self.reallocate_if_needed()
        if self.needs_update():
            self._formation_group.set_plains(self.prepare_plains())

        self._world_formation.draw()
        self._formation_group.render()

