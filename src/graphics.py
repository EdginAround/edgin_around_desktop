import ctypes
import math
import time

import numpy

from OpenGL import GL

from typing import Final, Iterable, Optional

from . import defs, geometry, media, skeleton


class SolidPolyhedronRenderer:
    def __init__(self, figure, texture_id) -> None:
        vertices = numpy.array(
            [value for vertex in figure.get_vertices() for value in vertex],
            dtype=numpy.float32
        )

        indices = numpy.array(
            [value for index in figure.get_triangles() for value in index],
            dtype=numpy.uint32
        )

        self.texture_id = texture_id
        self.index_count = len(indices)

        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ibo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL.GL_STATIC_DRAW)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def __del__(self) -> None:
        GL.glDeleteBuffers(2, [self.vbo, self.ibo])

    def render(self) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glDrawElements(GL.GL_TRIANGLES, 4 * self.index_count, GL.GL_UNSIGNED_INT, None)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)


class PlainRenderer:
    def __init__(self, radius, theta, phi, bearing, texture_id, actor_id) -> None:
        self.radius = radius
        self.theta = theta
        self.phi = phi
        self.texture_id = texture_id
        self.actor_id = actor_id
        self.bearing = bearing

        self.highlight = False

        self.cam_left: Optional[float] = None
        self.cam_bottom: Optional[float] = None
        self.cam_right: Optional[float] = None
        self.cam_top: Optional[float] = None
        self.cam_dist = 0.0

        self.vbo = GL.glGenBuffers(1)
        self.ibo = GL.glGenBuffers(1)

        self._load_vertices()
        self._load_indices()

    def __del__(self) -> None:
        GL.glDeleteBuffers(2, [self.vbo, self.ibo])

    def set_highlight(self, highlight: bool) -> None:
        self.highlight = highlight

    def get_camera_distance(self) -> float:
        return self.cam_dist

    def render(self, loc_highlight) -> None:
        GL.glUniform1i(loc_highlight, int(self.highlight))
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 20, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 20, ctypes.c_void_p(12))
        GL.glEnableVertexAttribArray(1)

        GL.glDrawElements(GL.GL_TRIANGLES, 4 * self.index_count, GL.GL_UNSIGNED_INT, None)

        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def change_position(self, radius, theta, phi, bearing) -> None:
        self.radius = radius
        self.theta = theta
        self.phi = phi
        self.bearing = bearing
        self._load_vertices()

    def change_bearing(self, bearing) -> None:
        self.bearing = bearing
        self._load_vertices()

    def calculate_screen_bounds(self, mvp) -> None:
        left_bottom, right_top = mvp @ self.corners[0], mvp @ self.corners[3]
        self.cam_left = left_bottom[0] / left_bottom[3]
        self.cam_bottom = left_bottom[1] / left_bottom[3]
        self.cam_right = right_top[0] / right_top[3]
        self.cam_top = right_top[1] / right_top[3]
        self.cam_dist = left_bottom[2] / left_bottom[3]

    def get_boundary(self) -> geometry.Boundary2D:
        assert self.cam_left is not None
        assert self.cam_bottom is not None
        assert self.cam_right is not None
        assert self.cam_top is not None
        return geometry.Boundary2D(self.cam_left, self.cam_bottom, self.cam_right, self.cam_top)

    def _load_vertices(self) -> None:
        vertices = self._prepare_vertices()
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL.GL_DYNAMIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def _load_indices(self) -> None:
        indices = numpy.array([0, 1, 2, 2, 1, 3], dtype=numpy.uint32)
        self.index_count = len(indices)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

    def _prepare_vertices(self) -> numpy.array:
        pos = geometry.Coordinates.spherical_to_cartesian(self.radius, self.theta, self.phi)

        self.pos = numpy.array((*pos, 1.0), dtype=numpy.float32).reshape(4, 1)

        transformation = geometry.Matrices3D.translation(pos) \
                       @ geometry.Matrices3D.personal_to_global(self.theta, self.phi, self.bearing)

        self.corners = [(transformation @ numpy.array(o).reshape(4, 1)) for o in (
            (-0.5, 0.0, 0.0, 1.0),
            ( 0.5, 0.0, 0.0, 1.0),
            (-0.5, 1.0, 0.0, 1.0),
            ( 0.5, 1.0, 0.0, 1.0),
        )]

        return numpy.array([
            *self.corners[0][:3], 0.0, 1.0,
            *self.corners[1][:3], 1.0, 1.0,
            *self.corners[2][:3], 0.0, 0.0,
            *self.corners[3][:3], 1.0, 0.0,
        ], dtype=numpy.float32)


class SkeletonRenderer:
    DEFAULT_ANIMATION = 'idle'

    def __init__(self, skinset: media.Textures, skeleton: skeleton.Skeleton) -> None:
        self._skinset = skinset
        self._skeleton = skeleton

        self._vao = GL.glGenVertexArrays(1)
        self._vbo = GL.glGenBuffers(1)
        self._ibo = GL.glGenBuffers(1)

        self._bind()
        self._load_indices()
        self._unbind()

        self._start_moment = time.monotonic()
        self._animation_name: str = ''
        self.select_animation(self.DEFAULT_ANIMATION)

    def select_animation(self, name: str) -> None:
        if name != self._animation_name:
            self._start_moment = time.monotonic()
            self._animation = self._skeleton.get_animation(name)
            if self._animation is None:
                print(f'Animation "{name}" not found')
                self._animation = self._skeleton.get_animation(self.DEFAULT_ANIMATION)
                self._animation_name = self.DEFAULT_ANIMATION
            else:
                self._animation_name = name

    def render(self) -> None:
        assert self._animation is not None

        stride: Final[int] = 6

        interval = time.monotonic() - self._start_moment
        if not self._animation.is_looped() and interval > self._animation.get_length():
            self.select_animation(self.DEFAULT_ANIMATION)
            interval = 0.0

        self._bind()

        tiles = self._animation.tick(interval, self._skeleton.get_sources())
        self._load_vertices(tiles)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 20, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 20, ctypes.c_void_p(12))
        GL.glEnableVertexAttribArray(1)

        for i, tile in enumerate(tiles):
            texture_id = self._skinset[tile.name]
            if texture_id is not None:
                GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
                GL.glDrawElements(
                        GL.GL_TRIANGLES,
                        stride,
                        GL.GL_UNSIGNED_INT,
                        ctypes.c_void_p(4 * stride * i),
                    )

        GL.glDisableVertexAttribArray(1)
        GL.glDisableVertexAttribArray(0)

        self._unbind()

    def _bind(self) -> None:
        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._ibo)

    def _unbind(self) -> None:
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def _load_vertices(self, tiles: Iterable[geometry.Tile]) -> None:
        vertices = self._prepare_vertices(tiles)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL.GL_DYNAMIC_DRAW)

    def _load_indices(self) -> None:
        indices = self._prepare_indices()
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL.GL_STATIC_DRAW)

    def _prepare_vertices(self, tiles: Iterable[geometry.Tile]) -> numpy.array:
        SEPARATION = 0.001
        data = []
        for i, tile in enumerate(tiles):
            data.append([
                    tile.points[0][0], tile.points[0][1], SEPARATION * i, 0.0, 1.0,
                    tile.points[1][0], tile.points[1][1], SEPARATION * i, 0.0, 0.0,
                    tile.points[2][0], tile.points[2][1], SEPARATION * i, 1.0, 0.0,
                    tile.points[3][0], tile.points[3][1], SEPARATION * i, 1.0, 1.0,
                ])
        return numpy.array(data, dtype=numpy.float32).flatten()

    def _prepare_indices(self) -> numpy.array:
        num_layers = self._skeleton.get_max_num_layers()
        return numpy.array([
                4 * num + offset for num in range(num_layers) for offset in (0, 1, 2, 2, 3, 0)
            ], dtype=numpy.uint32)


class PositionedSkeletonRenderer:
    def __init__(self,
            skinset: media.Textures,
            skeleton: skeleton.Skeleton,
            radius: float,
            theta: float,
            phi: float,
            bearing: float,
            actor_id: defs.ActorId,
            view: numpy.array,
        ) -> None:
        self._highlight = False
        self._actor_id = actor_id
        self._skeleton = skeleton
        self._render = SkeletonRenderer(skinset, skeleton)
        self.change_position_and_view(radius, theta, phi, bearing, view)

    def set_highlight(self, highlight: bool) -> None:
        self._highlight = highlight

    def change_position(self, radius: float, theta: float, phi: float, bearing: float) -> None:
        self._update_position(radius, theta, phi, bearing)
        self._calculate_screen_bounds()

    def change_view(self, view: numpy.array) -> None:
        self._update_view(view)
        self._calculate_screen_bounds()

    def change_position_and_view(
            self,
            radius: float,
            theta: float,
            phi: float,
            bearing: float,
            view: numpy.array,
        ) -> None:
        self._update_position(radius, theta, phi, bearing)
        self._update_view(view)
        self._calculate_screen_bounds()

    def select_animation(self, name: str) -> None:
        self._render.select_animation(name)

    def get_camera_distance(self) -> float:
        return self._cam_dist

    def get_actor_id(self) -> defs.ActorId:
        return self._actor_id

    def reacts_to(self, x: float, y: float) -> bool:
        assert self._cam_left is not None
        assert self._cam_bottom is not None
        assert self._cam_right is not None
        assert self._cam_top is not None

        return self._cam_left < x and x < self._cam_right \
           and self._cam_bottom < y and y < self._cam_top

    def render(self, loc_highlight, loc_model) -> None:
        self._setup_rendering(loc_highlight, loc_model)
        self._render.render()

    def _update_position(self, radius: float, theta: float, phi: float, bearing: float) -> None:
        self._radius = radius
        self._theta = theta
        self._phi = phi
        self._bearing = bearing
        self._model = \
            geometry.Matrices3D.rotation_x(-0.5 * math.pi) @ \
            geometry.Matrices3D.rotation_z(self._phi) @ \
            geometry.Matrices3D.rotation_x(self._theta) @ \
            geometry.Matrices3D.rotation_z(-self._bearing) @ \
            geometry.Matrices3D.translation((0.0, 0.0, self._radius)) @\
            geometry.Matrices3D.rotation_x(0.5 * math.pi)

    def _update_view(self, view: numpy.array) -> None:
        self._view = view

    def _calculate_screen_bounds(self) -> None:
        left = self._skeleton.get_interaction().hover_area.left
        right = self._skeleton.get_interaction().hover_area.right
        top = self._skeleton.get_interaction().hover_area.top
        bottom = self._skeleton.get_interaction().hover_area.bottom

        trans = self._view @ self._model
        left_bottom = (trans @ numpy.array((left, bottom, 0.0, 1.0)).reshape(4, 1)).flatten()
        right_top = (trans @ numpy.array((right, top, 0.0, 1.0)).reshape(4, 1)).flatten()
        center = (trans @ numpy.array((0.0, 0.0, 0.0, 1.0)).reshape(4, 1)).flatten()

        self._cam_left = left_bottom[0] / left_bottom[3]
        self._cam_bottom = left_bottom[1] / left_bottom[3]
        self._cam_right = right_top[0] / right_top[3]
        self._cam_top = right_top[1] / right_top[3]
        self._cam_dist = center[2] / center[3]

    def _setup_rendering(self, loc_highlight: int, loc_model: int) -> None:
        GL.glUniform1i(loc_highlight, int(self._highlight))
        GL.glUniformMatrix4fv(loc_model, 1, GL.GL_TRUE, self._model)

