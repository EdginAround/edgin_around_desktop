import math
import numpy
import ctypes

from OpenGL import GL

from typing import Optional

from . import geometry


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
        self.vbo = GL.glGenBuffers(1)
        self.ibo = GL.glGenBuffers(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

    def __del__(self) -> None:
        GL.glDeleteBuffers(2, [self.vbo, self.ibo])

    def render(self) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glDrawElements(GL.GL_TRIANGLES, 4 * self.index_count, GL.GL_UNSIGNED_INT, None)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)


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

    def set_highlight(self, highlight) -> None:
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

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

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

        transformation = geometry.Matrices.translation(pos) \
                       @ geometry.Matrices.personal_to_global(self.theta, self.phi, self.bearing)

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

