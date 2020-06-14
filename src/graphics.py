import numpy
import ctypes

from OpenGL.GL import *

class SolidPolyhedronRenderer:
    def __init__(self, figure):
        vertices = numpy.array(
            [value for vertex in figure.get_vertices() for value in vertex],
            dtype=numpy.float32
        )

        indices = numpy.array(
            [value for index in figure.get_triangles() for value in index],
            dtype=numpy.uint32
        )

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
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawElements(GL_TRIANGLES, 4 * self.index_count, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

class PlainRenderer:
    def __init__(self, pos):
        self.pos = pos

        offset = 0.0
        vertices = numpy.array(
            [
                 pos[0] + 0.5, pos[1], pos[2] + 0.0, 1.0, 1.0,
                 pos[0] + 0.5, pos[1], pos[2] + 1.0, 1.0, 0.0,
                 pos[0] - 0.5, pos[1], pos[2] + 0.0, 0.0, 1.0,
                 pos[0] - 0.5, pos[1], pos[2] + 1.0, 0.0, 0.0
            ],
            dtype=numpy.float32
        )

        indices = numpy.array([0, 1, 2, 1, 2, 3], dtype=numpy.uint32)

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
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, None)
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glDrawElements(GL_TRIANGLES, 4 * self.index_count, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

