import ctypes, math, time
import numpy

from OpenGL import GL

from typing import Final, Iterable, List, Optional

from . import defs, formations, geometry, media, skeleton


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

        self._texture_id = texture_id
        self._index_count = len(indices)

        self._vao = GL.glGenVertexArrays(1)
        self._vbo = GL.glGenBuffers(1)
        self._ibo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._ibo)

        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL.GL_STATIC_DRAW)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def __del__(self) -> None:
        GL.glDeleteBuffers(2, [self._vbo, self._ibo])

    def render(self) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)

        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._ibo)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glDrawElements(GL.GL_TRIANGLES, 4 * self._index_count, GL.GL_UNSIGNED_INT, None)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)


class SkeletonRenderer:
    DEFAULT_ANIMATION = 'idle'

    def __init__(self, skeleton: skeleton.Skeleton) -> None:
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
            selected = self._skeleton.select_animation(name)
            if not selected:
                print(f'Animation "{name}" not found')
                self._skeleton.select_default_animation()
                self._animation_name = self.DEFAULT_ANIMATION
            else:
                self._animation_name = name

    def get_skeleton(self) -> skeleton.Skeleton:
        return self._skeleton

    def attach_skeleton(
            self,
            element_name: str,
            source_skeleton: Optional[skeleton.Skeleton]):
        self._skeleton.attach_skeleton(element_name, source_skeleton)

    def __del__(self) -> None:
        GL.glDeleteBuffers(2, [self._vbo, self._ibo])

    def render(self, skins: media.Skins) -> None:
        assert self._skeleton.has_selected_animation()

        stride: Final[int] = 6

        interval = time.monotonic() - self._start_moment
        if not self._skeleton.is_animation_looped() \
        and interval > self._skeleton.get_animation_length():
            self._skeleton.select_default_animation()
            interval = 0.0

        self._bind()

        tiles = self._skeleton.tick(interval)
        self._load_vertices(tiles)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 20, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 20, ctypes.c_void_p(12))
        GL.glEnableVertexAttribArray(1)

        for i, tile in enumerate(tiles):
            texture_id = skins.get(tile.id)
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
            skeleton: skeleton.Skeleton,
            radius: float,
            theta: float,
            phi: float,
            bearing: float,
            actor_id: defs.ActorId,
            view: numpy.array,
        ) -> None:
        self._highlight = False
        self._is_visible = True
        self._actor_id = actor_id
        self._skeleton = skeleton
        self._render = SkeletonRenderer(skeleton)
        self.change_position_and_view(radius, theta, phi, bearing, view)

    def set_highlight(self, highlight: bool) -> None:
        self._highlight = highlight

    def set_visibility(self, is_visible: bool) -> None:
        self._is_visible = is_visible

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

    def is_visible(self) -> bool:
        return self._is_visible

    def get_skeleton(self) -> skeleton.Skeleton:
        return self._render.get_skeleton()

    def attach_skeleton(
            self,
            element_name: str,
            source_skeleton: Optional[skeleton.Skeleton]):
        self._render.attach_skeleton(element_name, source_skeleton)

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

    def render(self, loc_highlight, loc_model, skins: media.Skins) -> None:
        self._setup_rendering(loc_highlight, loc_model)
        self._render.render(skins)

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
            geometry.Matrices3D.translation((0.0, 0.0, self._radius)) @ \
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


class Fbo:
    def __init__(self) -> None:
        self._fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)

        if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
            print('Framebuffer not complete')

        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        self._texture_color = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_color)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

        self._texture_depth = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_depth)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def get_color_texture_id(self) -> int:
        return self._texture_color

    def attach(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)
        GL.glFramebufferTexture2D(
                GL.GL_FRAMEBUFFER,
                GL.GL_COLOR_ATTACHMENT0,
                GL.GL_TEXTURE_2D,
                self._texture_color,
                0,
            )
        GL.glFramebufferTexture2D(
                GL.GL_FRAMEBUFFER,
                GL.GL_DEPTH_ATTACHMENT,
                GL.GL_TEXTURE_2D,
                self._texture_depth,
                0,
            )

    def detach(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def resize(self, width: float, height: float) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_color)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, ctypes.c_void_p(0)
        )

        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_depth)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, width, height, 0,
            GL.GL_DEPTH_COMPONENT, GL.GL_UNSIGNED_BYTE, ctypes.c_void_p(0)
        )

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def __enter__(self) -> 'Fbo':
        self.attach()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.detach()

