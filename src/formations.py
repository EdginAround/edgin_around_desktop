import math, numbers

from enum import Enum

from typing import List, Optional, Tuple, Union

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


class EventResult(Enum):
    NOT_HANDLED = 0
    HANDLED = 1


class Position:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(a: 'Position', b: 'Position') -> 'Position':
        return Position(a.x + b.x, a.y + b.y)

    def __sub__(a: 'Position', b: 'Position') -> 'Position':
        return Position(a.x - b.x, a.y - b.y)

    def __repr__(self) -> str:
        return f'Position(x: {self.x}, y: {self.y})'


class Size:
    def __init__(self, width: float, height: float) -> None:
        self.width = max(width, 0.0)
        self.height = max(height, 0.0)

    def __repr__(self) -> str:
        return f'Size(width: {self.width}, height: {self.height})'


class Color:
    def __init__(self, r: float, g: float, b: float, a: float):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_256_tuple(self) -> Tuple[int, int, int, int]:
        return (int(255 * self.r), int(255 * self.g), int(255 * self.b), int(255 * self.a))

    def to_float_tuple(self) -> Tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    def __repr__(self) -> str:
        return f'Color({self.r}, {self.g}, {self.b}, {self.a})'


class Plain:
    def __init__(
            self,
            texture_id: Optional[int],
            color: Optional[Color],
            position: Position,
            size: Size,
            flip_vertical: bool = False,
        ) -> None:
        self.texture_id = texture_id
        self.color = color
        self.position = position
        self.size = size
        self.flip_vertical = flip_vertical

    def __repr__(self) -> str:
        return 'Plain(texture_id: {}, color: {}, position: {}, size: {}, flip_vertical: {})' \
        .format(self.texture_id, self.color, str(self.position), str(self.size), self.flip_vertical)


class Content:
    def __init__(
            self,
            size: Size,
            texture_id: Optional[int] = None,
            color: Optional[Color] = None,
        ) -> None:
        self._texture_id = texture_id
        self._color = color
        self._size = size

    def has_proper_size(self) -> bool:
        return (not math.isclose(self._size.width, 0.0)) \
           and (not math.isclose(self._size.height, 0.0))

    def has_proper_content(self) -> bool:
        return (self._color is not None) or (self._texture_id is not None)

    def is_displayable(self) -> bool:
        return self.has_proper_size() and self.has_proper_content()

    def get_size(self) -> Size:
        return self._size

    def get_texture_id(self) -> Optional[int]:
        return self._texture_id

    def get_color(self) -> Optional[Color]:
        return self._color

    def _set_size(self, size: Size) -> None:
        self._size = size

    def __repr__(self) -> str:
        return 'Content(size: {}, texture: {}, color: {})' \
            .format(self._size, self._texture_id, self._color)


class Formation:
    def __init__(self) -> None:
        self._children: List[Formation] = list()
        self._position = Position(0.0, 0.0)
        self._size = Size(0.0, 0.0)
        self._content: Optional[Content] = None
        self._flip_vertical = False
        self._is_visible = True
        self._needs_update = False
        self._needs_reallocation = True

    def get_position(self) -> Position:
        return self._position

    def get_size(self) -> Size:
        return self._size

    def get_content(self) -> Optional[Content]:
        return self._content

    def get_is_visible(self) -> bool:
        return self._is_visible

    def set_content(self, content: Optional[Content]) -> None:
        self._content = content

    def set_position(self, position: Position) -> None:
        self._position = position

    def set_is_visible(self, is_visible: bool) -> None:
        self._is_visible = is_visible
        if is_visible:
            self._needs_reallocation = True

    def clear(self) -> None:
        self._children = list()
        self.mark_as_needs_reallocation()

    def resize(self, size: Size) -> bool:
        result = False
        if self._size != size:
            self._size = size
            self.mark_as_needs_reallocation()
            result = True

        if self.needs_reallocation():
            self.reallocate()

        return result

    def reallocate(self) -> None:
        self._needs_reallocation = False
        self._needs_update = True

    def mark_as_needs_update(self) -> None:
        self._needs_update = True

    def mark_as_needs_reallocation(self) -> None:
        self._needs_reallocation = True

    def needs_update(self) -> bool:
        return self._is_visible and \
            (self._needs_update or any(c.needs_update() for c in self._children))

    def needs_reallocation(self) -> bool:
        return self._is_visible and \
            (self._needs_reallocation or any(c.needs_reallocation() for c in self._children))

    def on_grab(self, position: Position, *args) -> EventResult:
        if self.contains(position):
            for child in self._children[::-1]:
                if child._is_visible:
                    relative_position = position - child.get_position()
                    if child.contains(relative_position):
                        if child.on_grab(relative_position, *args) == EventResult.HANDLED:
                            return EventResult.HANDLED
        return EventResult.NOT_HANDLED

    def on_release(self, position: Position, *args) -> EventResult:
        if self.contains(position):
            for child in self._children[::-1]:
                if child._is_visible:
                    relative_position = position - child.get_position()
                    if child.contains(relative_position):
                        if child.on_release(relative_position, *args) == EventResult.HANDLED:
                            return EventResult.HANDLED
        return EventResult.NOT_HANDLED

    def on_scroll(self) -> None:
        pass

    def calc_pref_width(self, height: float) -> float:
        if (self._content is not None) and self._content.has_proper_size():
            return self._content._size.width * height / self._content._size.height
        else:
            return 0.0

    def calc_pref_height(self, width: float) -> float:
        if (self._content is not None) and self._content.has_proper_size():
            return self._content._size.height * width / self._content._size.width
        else:
            return 0.0

    def reallocate_if_needed(self) -> None:
        if self.needs_reallocation():
            self.reallocate()

    def prepare_plains(self, parent_position=Position(0.0, 0.0)) -> List[Plain]:
        abs_position = self._position + parent_position
        result = list()

        if self._is_visible:
            if (self._content is not None) and (self._content.is_displayable()):
                result.append(Plain(
                        self._content._texture_id,
                        self._content._color,
                        abs_position,
                        self._size,
                        self._flip_vertical,
                    ))

            for child in self._children:
                result.extend(child.prepare_plains(abs_position))

        self._needs_update = False
        return result

    def contains(self, position: Position) -> bool:
        x1, x2 = 0.0, self._size.width
        y1, y2 = 0.0, self._size.height
        x0, y0 = position.x, position.y
        return (x1 < x0) and (x0 < x2) and (y1 < y0) and (y0 < y2)


class Stripe(Formation):
    def __init__(self, orientation: Orientation) -> None:
        super().__init__()
        self._orientation = orientation

    def get_orientation(self) -> Orientation:
        return self._orientation

    def append(self, child: Formation) -> None:
        self._children.append(child)
        self.mark_as_needs_reallocation()

    def prepend(self, child: Formation) -> None:
        self._children.insert(0, child)
        self.mark_as_needs_reallocation()

    def insert(self, index: int, child: Formation) -> None:
        self._children.insert(index, child)
        self.mark_as_needs_reallocation()

    def reallocate(self) -> None:
        super().reallocate()

        if self._orientation == Orientation.VERTICAL:
            self._reallocate_vertical()

        elif self._orientation == Orientation.HORIZONTAL:
            self._reallocate_horizontal()

    def _reallocate_vertical(self) -> None:
        size = self.get_size()
        pref_heights = [child.calc_pref_height(size.width) for child in self._children]
        sum_heights = sum(pref_heights)
        height_left = size.height - sum_heights
        space = (height_left / (len(self._children) - 1)) if (len(self._children) > 1) else 0

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
            return sum(child.calc_pref_width(height) for child in self._children)

        elif self._orientation == Orientation.VERTICAL:
            return max(child.calc_pref_width(height) for child in self._children)

        else:
            raise Exception('Wrong orentation')

    def calc_pref_height(self, width: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            return max(child.calc_pref_height(width) for child in self._children)

        elif self._orientation == Orientation.VERTICAL:
            return sum(child.calc_pref_height(width) for child in self._children)

        else:
            raise Exception('Wrong orientation')


class Lineup(Formation):
    class Pack:
        def __init__(self, weight: float) -> None:
            self.weight = float(weight)

        def __repr__(self) -> str:
            return f'Pack({self.weight})'

    def __init__(self, orientation: Orientation) -> None:
        super().__init__()
        self._orientation = orientation
        self._packs: List[Lineup.Pack] = list()

    def get_orientation(self) -> Orientation:
        return self._orientation

    def append(self, child: Formation, pack: Pack) -> None:
        self._children.append(child)
        self._packs.append(pack)
        self.mark_as_needs_reallocation()

    def prepend(self, child: Formation, pack: Pack) -> None:
        self._children.insert(0, child)
        self._packs.insert(0, pack)
        self.mark_as_needs_reallocation()

    def insert(self, index: int, child: Formation, pack: Pack) -> None:
        self._children.insert(index, child)
        self._packs.insert(index, pack)
        self.mark_as_needs_reallocation()

    def clear(self) -> None:
        super().clear()
        self._packs = list()

    def reallocate(self) -> None:
        super().reallocate()

        if self._orientation == Orientation.VERTICAL:
            self._reallocate_vertical()

        elif self._orientation == Orientation.HORIZONTAL:
            self._reallocate_horizontal()

    def _reallocate_vertical(self) -> None:
        size = self.get_size()
        all_weights = sum(pack.weight for pack in self._packs)

        heights_and_packs: List[Union[float, Lineup.Pack]] = []
        pref_heights = 0.0
        for child, pack in zip(self._children, self._packs):
            if pack.weight == 0.0:
                pref_height = float(child.calc_pref_height(size.width))
                pref_heights += pref_height
                heights_and_packs.append(pref_height)
            else:
                heights_and_packs.append(pack)

        height_left = size.height - pref_heights
        heights: List[float] = []
        for data in heights_and_packs:
            if isinstance(data, self.Pack):
                heights.append(height_left * data.weight / all_weights)
            elif isinstance(data, numbers.Number):
                heights.append(data)

        y = 0.0
        for child, height in zip(self._children, heights):
            child.resize(Size(size.width, height))
            child.set_position(Position(0, y))
            y += height

    def _reallocate_horizontal(self) -> None:
        size = self.get_size()
        all_weights = sum(pack.weight for pack in self._packs)

        widths_and_packs: List[Union[float, Lineup.Pack]] = []
        pref_widths = 0.0
        for child, pack in zip(self._children, self._packs):
            if pack.weight == 0.0:
                pref_width = float(child.calc_pref_width(size.height))
                pref_widths += pref_width
                widths_and_packs.append(pref_width)
            else:
                widths_and_packs.append(pack)

        width_left = size.width - pref_widths
        widths: List[float] = []
        for data in widths_and_packs:
            if isinstance(data, self.Pack):
                widths.append(width_left * data.weight / all_weights)
            elif isinstance(data, numbers.Number):
                widths.append(data)

        x = 0.0
        for child, width in zip(self._children, widths):
            child.resize(Size(width, size.height))
            child.set_position(Position(x, 0))
            x += width

    def calc_pref_width(self, height: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            return sum(child.calc_pref_width(height) for child in self._children)

        elif self._orientation == Orientation.VERTICAL:
            return max(child.calc_pref_width(height) for child in self._children)

        else:
            raise Exception('Wrong orientation')

    def calc_pref_height(self, width: float) -> float:
        if self._orientation == Orientation.HORIZONTAL:
            return max(child.calc_pref_height(width) for child in self._children)

        elif self._orientation == Orientation.VERTICAL:
            return sum(child.calc_pref_height(width) for child in self._children)

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
        self.mark_as_needs_reallocation()

    def clear(self) -> None:
        super().clear()
        self._children = [Formation() for i in range(self._rows * self._columns)]

    def reallocate(self) -> None:
        super().reallocate()

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


class Stack(Formation):
    def __init__(self) -> None:
        super().__init__()

    def reallocate(self) -> None:
        super().reallocate()

        for child in self._children:
            child.resize(self.get_size())

    def calc_pref_width(self, height: float) -> float:
        return max(child.calc_pref_width(height) for child in self._children)

    def calc_pref_height(self, width: float) -> float:
        return max(child.calc_pref_height(width) for child in self._children)

    def add(self, child: Formation) -> None:
        self._children.append(child)


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

    def clear(self) -> None:
        super().clear()
        self._constraints = list()

    def reallocate(self) -> None:
        super().reallocate()

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

    def _calc_position(self, gravity: Gravity, container_size: float, content_size: float) -> float:
        if gravity == Gravity.START:
            return 0.0

        elif gravity == Gravity.CENTER:
            return (container_size - content_size) / 2.0

        elif gravity == Gravity.END:
            return container_size - content_size

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
    def __init__(self, orientation: Orientation, gravity: Gravity) -> None:
        super().__init__()
        self._inner = Stripe(orientation)
        self._children = [self._inner]
        self._offset = Position(0.0, 0.0)
        self._gravity = gravity

    def append(self, child: Formation) -> None:
        self._inner.append(child)
        self.mark_as_needs_reallocation()

    def prepend(self, child: Formation) -> None:
        self._inner.prepend(child)
        self.mark_as_needs_reallocation()

    def insert(self, index: int, child: Formation) -> None:
        self._inner.insert(index, child)
        self.mark_as_needs_reallocation()

    def clear(self) -> None:
        self._inner.clear()
        self.mark_as_needs_reallocation()

    def reallocate(self) -> None:
        super().reallocate()

        orientation = self._inner.get_orientation()
        if orientation == Orientation.VERTICAL:
            self._reallocate_vertical()
        elif orientation == Orientation.HORIZONTAL:
            self._reallocate_horizontal()

    def _reallocate_vertical(self) -> None:
        content_height = self._inner.calc_pref_height(self._size.width)
        offset_y = max(min(self._offset.y, self._size.height - content_height), 0.0)
        position = self._calc_position(self._size.height, content_height, offset_y)
        self._offset = Position(self._offset.x, offset_y)
        self._inner.set_position(Position(0.0, position))
        self._inner.resize(Size(self._size.width, content_height))

    def _reallocate_horizontal(self) -> None:
        content_width = self._inner.calc_pref_width(self._size.height)
        offset_x = max(min(self._offset.x, self._size.width - content_width), 0.0)
        position = self._calc_position(self._size.width, content_width, offset_x)
        self._offset = Position(offset_x, self._offset.y)
        self._inner.set_position(Position(position, 0.0))
        self._inner.resize(Size(content_width, self._size.height))

    def _calc_position(self, container_size: float, content_size: float, offset: float) -> float:
        if self._gravity == Gravity.START:
            return offset
        elif self._gravity == Gravity.CENTER:
            return 0.5 * (container_size - content_size) + offset
        elif self._gravity == Gravity.END:
            return container_size - content_size + offset
        else:
            raise Exception('Unknown gravity')

    def calc_pref_width(self, height: float) -> float:
        return self._inner.calc_pref_width(height)

    def calc_pref_height(self, width: float) -> float:
        return self._inner.calc_pref_height(width)

    def on_grab(self, position: Position, *args) -> EventResult:
        return super().on_grab(position, *args)

