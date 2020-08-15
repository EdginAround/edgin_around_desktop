#!/usr/bin/env python

from typing import cast, List, Union

from . import formations, formations_images, formations_renderer
from . import defs, graphics, inventory, media, world


class WorldFormation(formations.Formation):
    def __init__(self, world: world.World) -> None:
        super().__init__()
        self._world = world
        self._fbo = graphics.Fbo()
        self._flip_vertical = True

    def resize(self, size: formations.Size) -> None:
        super().resize(size)

        size = self.get_size()
        width, height = int(size.width), int(size.height)

        self._fbo.resize(width, height)
        self._world.resize(width, height)

        content = formations.Content(self._fbo.get_color_texture_id(), size)
        self.set_content(content)

    def draw(self) -> None:
        with self._fbo:
            self._world.draw()


class MapFormation(formations.Formation):
    def __init__(self) -> None:
        super().__init__()

        content = formations_images.ImageFileContent('res/images/map.png')
        self.set_content(content)


class HandFormation(formations.Formation):
    def __init__(self) -> None:
        super().__init__()

    def set_image(self, texture_id: int) -> None:
        content = formations.Content(texture_id, formations.Size(100, 100))
        self.set_content(content)


class PocketFormation(formations.Formation):
    def __init__(self) -> None:
        super().__init__()

    def set_image(self, texture_id: int) -> None:
        content = formations.Content(texture_id, formations.Size(100, 100))
        self.set_content(content)


class PocketsFormation(formations.Grid):
    ROWS = 2
    COLUMS = 10

    def __init__(self) -> None:
        super().__init__(self.ROWS, self.COLUMS)

        self.pockets = [[PocketFormation() for i in range(self.COLUMS)] for j in range(self.ROWS)]
        for i, row in enumerate(self.pockets):
            for j, pocket in enumerate(row):
                self.insert(pocket, i, j)

    def get_pocket(self, index: int) -> PocketFormation:
        return cast(PocketFormation, self.get(index))


class InventoryFormation(formations.Stripe):
    LEFT_HAND = 'left_hand'
    RIGHT_HAND = 'right_hand'
    EMPTY_SLOT = 'empty_slot'

    def __init__(self, tex: media.Textures) -> None:
        super().__init__(formations.Orientation.HORIZONTAL)

        self.left_hand = HandFormation()
        self.pockets = PocketsFormation()
        self.right_hand = HandFormation()

        self.left_hand.set_image(tex[self.LEFT_HAND])
        self.right_hand.set_image(tex[self.RIGHT_HAND])

        self.append(self.left_hand)
        self.append(self.pockets)
        self.append(self.right_hand)

    def set_inventory(self, inventory: inventory.Inventory, tex: media.Textures) -> None:
        image = inventory.left_hand.image if inventory.left_hand is not None else self.LEFT_HAND
        self.left_hand.set_image(tex[image])

        image = inventory.right_hand.image if inventory.right_hand is not None else self.RIGHT_HAND
        self.right_hand.set_image(tex[image])

        for i, entry in enumerate(inventory.entries):
            image = entry.image if entry is not None else self.EMPTY_SLOT
            self.pockets.get_pocket(i).set_image(tex[image])

        self.reallocate()


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


class Gui(formations.Clasp):
    def __init__(self, world: world.World) -> None:
        from .formations import Expanse, Gravity, Orientation

        super().__init__()

        self._world = world
        self._formation_group = formations_renderer.FormationGroup()

        self._media = media.Media()
        self._media.load_inventory()

        self._world_formation = WorldFormation(world)
        self._map_formation = MapFormation()
        self._stats_formation = StatsFormation()
        self._inventory_formation = InventoryFormation(self._media.tex)

        world_constraint = self.Constraint(
                orientation=Orientation.HORIZONTAL,
                stretch=1.0,
                expanse=Expanse.FILL,
                horizontal_gravity=Gravity.CENTER,
                vertical_gravity=Gravity.CENTER,
            )
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

        self.add(self._world_formation, world_constraint)
        self.add(self._map_formation, map_constraint)
        self.add(self._stats_formation, stats_constraint)
        self.add(self._inventory_formation, inventory_constraint)

    def set_stats(self, stats: defs.Stats) -> None:
        self._stats_formation.set_stats(stats)

    def set_inventory(self, inventory: inventory.Inventory) -> None:
        self._inventory_formation.set_inventory(inventory, self._media.tex)
        self._update()

    def handle_resize(self, width: float, height: float) -> None:
        self.resize(formations.Size(width, height))
        self._formation_group.resize(width, height)
        self._update()

    def _update(self) -> None:
        self._formation_group.set_plains(self.prepare_plains())

    def handle_mouse_motion(self, x: float, y: float) -> None:
        # TODO: All mouse motion events are passed to `world` now. Pass them to all formations
        # and implement `enter` and `leave` events.
        self._world.highlight(x, y)

    def draw(self) -> None:
        self._world_formation.draw()
        self._formation_group.render()

