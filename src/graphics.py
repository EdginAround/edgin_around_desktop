import math
import numpy
import ctypes

from OpenGL.GL import *

from . import geometry

class SolidPolyhedronRenderer:
    def __init__(self, figure, texture):
        vertices = numpy.array(
            [value for vertex in figure.get_vertices() for value in vertex],
            dtype=numpy.float32
        )

        indices = numpy.array(
            [value for index in figure.get_triangles() for value in index],
            dtype=numpy.uint32
        )

        self.texture = texture
        self.index_count = len(indices)
        self.vbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def __del__(self):
        glDeleteBuffers(2, [self.vbo, self.ibo])

    def render(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawElements(GL_TRIANGLES, 4 * self.index_count, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

class PlainRenderer:
    def __init__(self, radius, theta, phi, bearing, texture):
        self.radius = radius
        self.theta = theta
        self.phi = phi
        self.bearing = bearing
        self.texture = texture

        self.highlight = False

        self.cam_left = None
        self.cam_bottom = None
        self.cam_right = None
        self.cam_top = None
        self.cam_dist = None

        self.vbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)

        self._load_vertices()
        self._load_indices()

    def __del__(self):
        glDeleteBuffers(2, [self.vbo, self.ibo])

    def set_highlight(self, highlight):
        self.highlight = highlight

    def get_camera_distance(self):
        return self.cam_dist

    def render(self, loc_highlight):
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glUniform1i(loc_highlight, int(self.highlight))

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, None)
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glDrawElements(GL_TRIANGLES, 4 * self.index_count, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def change_position(self, radius, theta, phi, bearing):
        self.radius = radius
        self.theta = theta
        self.phi = phi
        self.bearing = bearing
        self._load_vertices()

    def change_bearing(self, bearing):
        self.bearing = bearing
        self._load_vertices()

    def calculate_screen_bounds(self, mvp):
        left_bottom, right_top = mvp @ self.corners[0], mvp @ self.corners[3]
        self.cam_left = left_bottom[0] / left_bottom[3]
        self.cam_bottom = left_bottom[1] / left_bottom[3]
        self.cam_right = right_top[0] / right_top[3]
        self.cam_top = right_top[1] / right_top[3]
        self.cam_dist = left_bottom[2] / left_bottom[3]

    def get_boundary(self):
        return geometry.Boundary2D(self.cam_left, self.cam_bottom, self.cam_right, self.cam_top)

    def _load_vertices(self):
        vertices = self._prepare_vertices()
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _load_indices(self):
        indices = numpy.array([0, 1, 2, 2, 1, 3], dtype=numpy.uint32)
        self.index_count = len(indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def _prepare_vertices(self):
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

