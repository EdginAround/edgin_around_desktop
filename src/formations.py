import math

from enum import Enum

from typing import List, Optional, Tuple

# TODO: Implement unit tests for formations.


class Gravity(Enum):
    START = 0
    CENTER = 1
    END = 2


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Expanse(Enum):
    FIT = 0
    FILL = 1


class Position:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(a: 'Position', b: 'Position') -> 'Position':
        return Position(a.x + b.x, a.y + b.y)

    def __sub__(a: 'Position', b: 'Position') -> 'Position':
        return Position(a.x - b.x, a.y - b.y)

    def __str__(self) -> str:
        return 'Position(x: {}, y: {})'.format(self.x, self.y)


class Size:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return 'Size(width: {}, height: {})'.format(self.width, self.height)


class Plain:
    def __init__(
            self,
            texture_id: int,
            position: Position,
            size: Size,
            flip_vertical: bool = False,
        ) -> None:
        self.texture_id = texture_id
        self.position = position
        self.size = size
        self.flip_vertical = flip_vertical

    def __str__(self) -> str:
        return 'Plain(texture_id: {}, position: {}, size: {}, flip_vertical: {})' \
            .format(self.texture_id, str(self.position), str(self.size), self.flip_vertical)


class Color:
    def __init__(self, r: float, g: float, b: float, a: float):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_256_tuple(self) -> Tuple[int, int, int, int]:
        return (int(256 * self.r), int(256 * self.g), int(256 * self.b),  int(256 * self.a))


class Content:
    def __init__(self, texture_id, size: Size) -> None:
        self.texture_id = texture_id
        self.size = size

    def is_valid(self) -> bool:
        return not math.isclose(self.size.width, 0.0) and not math.isclose(self.size.height, 0.0)

    def get_texture_id(self) -> int:
        return self.texture_id

    def _set_size(self, size: Size) -> None:
        self.size = size

    def __str__(self) -> str:
        return 'Position(texture: {}, size: {})'.format(self.texture_id, self.size)


class Formation:
    def __init__(self) -> None:
        self._children: List[Formation] = list()
        self._position = Position(0.0, 0.0)
        self._size = Size(0.0, 0.0)
        self._content: Optional[Content] = None
        self._flip_vertical = False

    def get_position(self) -> Position:
        return self._position

    def get_size(self) -> Size:
        return self._size

    def get_content(self) -> Optional[Content]:
        return self._content

    def set_content(self, content: Content) -> None:
        self._content = content

    def set_position(self, position: Position) -> None:
        self._position = position

    def resize(self, size: Size):
        self._size = size

    def on_click(self, position: Position) -> None:
        if self.contains(position):
            for child in self._children:
                relative_position = position - child.get_position()
                if child.contains(relative_position):
                    child.on_click(relative_position)
                    break

    def on_scroll(self) -> None:
        pass

    def calc_pref_width(self, height: float) -> float:
        if (self._content is not None) and self._content.is_valid():
            return self._content.size.width * height / self._content.size.height
        else:
            return 0.0

    def calc_pref_height(self, width: float) -> float:
        if (self._content is not None) and self._content.is_valid():
            return self._content.size.height * width / self._content.size.width
        else:
            return 0.0

    def prepare_plains(self, parent_position=Position(0.0, 0.0)) -> List[Plain]:
        abs_position = self._position + parent_position

        if self._content is not None:
            result = [Plain(self._content.texture_id, abs_position, self._size, self._flip_vertical)]
        else:
            result = list()

        for child in self._children:
            result.extend(child.prepare_plains(abs_position))

        return result

    def contains(self, position: Position) -> bool:
        x1, x2 = self._position.x, self._position.x + self._size.width
        y1, y2 = self._position.y, self._position.y + self._size.height
        x0, y0 = position.x, position.y
        return (x1 < x0) and (x0 < x2) and (y1 < y0) and (y0 < y2)


class Stripe(Formation):
    def __init__(self, orientation: Orientation) -> None:
        super().__init__()
        self._orientation = orientation

    def append(self, child: Formation) -> None:
        self._children.append(child)
        self.reallocate()

    def prepend(self, child: Formation) -> None:
        self._children.insert(0, child)
        self.reallocate()

    def insert(self, index: int, child: Formation) -> None:
        self._children.insert(index, child)
        self.reallocate()

    def resize(self, size: Size) -> None:
        super().resize(size)
        self.reallocate()

    def reallocate(self) -> None:
        if self._orientation == Orientation.VERTICAL:
            self._reallocate_vertical()

        elif self._orientation == Orientation.HORIZONTAL:
            self._reallocate_horizontal()

    def _reallocate_vertical(self) -> None:
        size = self.get_size()
        pref_heights = [child.calc_pref_height(size.width) for child in self._children]
        sum_heights = sum(pref_heights)
        height_left = size.height - sum_heights
        space = height_left / (len(self._children) - 1)

        y = 0.0
        for child, pref_height in zip(self._children, pref_heights):
            child.resize(Size(size.width, pref_height))
            child.set_position(Position(0, y))
            y += space + pref_height

    def _reallocate_horizontal(self) -> None:
        size = self.get_size()
        pref_widths = [child.calc_pref_width(size.height) for child in self._children]
        sum_widths = sum(pref_widths)
        width_left = size.width - sum_widths
        space = width_left / (len(self._children) - 1) if len(self._children) != 1 else 0.0

        x = 0.0
        for child, pref_width in zip(self._children, pref_widths):
            child.resize(Size(pref_width, size.height))
            child.set_position(Position(x, 0))
            x += space + pref_width

    def calc_pref_width(self, height: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            return self._size.width

        elif self._orientation == Orientation.VERTICAL:
            return max(child.calc_pref_width(height) for child in self._children)

        else:
            raise Exception('Wrong orentation')

    def calc_pref_height(self, width: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            return max(child.calc_pref_height(width) for child in self._children)

        elif self._orientation == Orientation.VERTICAL:
            return self._size.height

        else:
            raise Exception('Wrong orientation')


class Lineup(Formation):
    class Pack:
        def __init__(self, weight: float) -> None:
            self.weight = weight

    def __init__(self, orientation: Orientation) -> None:
        super().__init__()
        self._orientation = orientation
        self._packs: List[Lineup.Pack] = list()

    def append(self, child: Formation, pack: Pack) -> None:
        self._children.append(child)
        self._packs.append(pack)
        self.reallocate()

    def prepend(self, child: Formation, pack: Pack) -> None:
        self._children.insert(0, child)
        self._packs.insert(0, pack)
        self.reallocate()

    def insert(self, index: int, child: Formation, pack: Pack) -> None:
        self._children.insert(index, child)
        self._packs.insert(index, pack)
        self.reallocate()

    def resize(self, size: Size) -> None:
        super().resize(size)
        self.reallocate()

    def reallocate(self) -> None:
        if self._orientation == Orientation.VERTICAL:
            self._reallocate_vertical()

        elif self._orientation == Orientation.HORIZONTAL:
            self._reallocate_horizontal()

    def _reallocate_vertical(self) -> None:
        size = self.get_size()
        full_weight = sum(pack.weight for pack in self._packs)

        y = 0.0
        for child, pack in zip(self._children, self._packs):
            height = size.height * pack.weight / full_weight
            child.resize(Size(size.width, height))
            child.set_position(Position(0, y))
            y += height

    def _reallocate_horizontal(self) -> None:
        size = self.get_size()
        full_weight = sum(pack.weight for pack in self._packs)

        x = 0.0
        for child, pack in zip(self._children, self._packs):
            width = size.width * pack.weight / full_weight
            child.resize(Size(width, size.height))
            child.set_position(Position(x, 0))
            x += width

    def calc_pref_width(self, height: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            min_width = sum(child.calc_pref_width(height) for child in self._children)
            return max(self._size.width, min_width)

        elif self._orientation == Orientation.VERTICAL:
            return max(child.calc_pref_width(height) for child in self._children)

        else:
            raise Exception('Wrong orientation')

    def calc_pref_height(self, width: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            return max(child.calc_pref_height(width) for child in self._children)

        elif self._orientation == Orientation.VERTICAL:
            min_height = sum(child.calc_pref_height(width) for child in self._children)
            return max(self._size.height, min_height)

        else:
            raise Exception('Wrong orientation')


class Grid(Formation):
    def __init__(self, rows: int, columns: int) -> None:
        super().__init__()
        self._rows = rows
        self._columns = columns
        self._children = [Formation() for i in range(rows * columns)]

    def get(self, row: int, column: Optional[int] = None) -> Formation:
        if column is not None:
            return self._children[row * self._columns + column]
        else:
            return self._children[row]

    def insert(self, child: Formation, row: int, column: int) -> None:
        self._children[row * self._columns + column] = child
        self.reallocate()

    def resize(self, size: Size) -> None:
        super().resize(size)
        self.reallocate()

    def reallocate(self) -> None:
        slot_size = Size(self._size.width / self._columns, self._size.height / self._rows)

        for j in range(self._rows):
            for i in range(self._columns):
                slot = self._children[self._columns * j + i]
                slot.resize(slot_size)
                slot.set_position(Position(slot_size.width * i, slot_size.height * j))

    def calc_pref_width(self, height: float) -> float:
        slot_height = height / self._rows
        max_preferred_width = max(child.calc_pref_width(slot_height) for child in self._children)
        return max_preferred_width * self._columns

    def calc_pref_height(self, width: float) -> float:
        slot_width = width / self._columns
        max_preferred_height = max(child.calc_pref_height(slot_width) for child in self._children)
        return max_preferred_height * self._rows


class Clasp(Formation):
    class Constraint:
        def __init__(
                self,
                orientation: Orientation,
                stretch: float,
                expanse: Expanse,
                horizontal_gravity: Gravity,
                vertical_gravity: Gravity,
                ) -> None:
            self.orientation = orientation
            self.stretch = stretch
            self.expanse = expanse
            self.horizontal_gravity = horizontal_gravity
            self.vertical_gravity = vertical_gravity

    def __init__(self) -> None:
        super().__init__()
        self._constraints: List[Clasp.Constraint] = list()

    def add(self, child: Formation, constraint: Constraint) -> None:
        self._children.append(child)
        self._constraints.append(constraint)

    def resize(self, size: Size) -> None:
        super().resize(size)
        self.reallocate()

    def reallocate(self) -> None:
        for child, constraint in zip(self._children, self._constraints):
            if constraint.orientation == Orientation.VERTICAL:
                size = self._calc_size_for_vertical(child, constraint)

            elif constraint.orientation == Orientation.HORIZONTAL:
                size = self._calc_size_for_horizontal(child, constraint)

            x = self._calc_position(constraint.horizontal_gravity, self._size.width, size.width)
            y = self._calc_position(constraint.vertical_gravity, self._size.height, size.height)
            position = Position(x, y)

            child.set_position(position)
            child.resize(size)

    def _calc_position(self, gravity: Gravity, big_size: float, small_size: float) -> float:
        if gravity == Gravity.START:
            return 0.0

        elif gravity == Gravity.CENTER:
            return (big_size - small_size) / 2.0

        elif gravity == Gravity.END:
            return big_size - small_size

        else:
            raise Exception('Wrong gravity')

    def _calc_size_for_horizontal(self, child: Formation, constraint: Constraint) -> Size:
        height = min(1.0, constraint.stretch) * self._size.height

        if constraint.expanse == Expanse.FILL:
            width = self._size.width
        else:
            width = child.calc_pref_width(height)

        return Size(width, height)

    def _calc_size_for_vertical(self, child: Formation, constraint: Constraint) -> Size:
        width = min(1.0, constraint.stretch) * self._size.width

        if constraint.expanse == Expanse.FILL:
            height = self._size.height
        else:
            height = child.calc_pref_height(width)

        return Size(width, height)


class Scroll(Formation):
    def __init__(self) -> None:
        super().__init__()

    def resize(self, size: Size) -> None:
        super().resize(size)
        self.reallocate()

    def reallocate(self) -> None:
        pass

