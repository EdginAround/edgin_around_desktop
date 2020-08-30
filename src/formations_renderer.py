import ctypes
import numpy

from OpenGL import GL
from OpenGL.GL import shaders

from typing import Final, List, Optional, Tuple

from . import formations, geometry


class PlainRenderer:
    def __init__(self) -> None:
        self._plains: List[formations.Plain] = list()

        self._vao = GL.glGenVertexArrays(1)
        self._vbo = GL.glGenBuffers(1)
        self._ibo = GL.glGenBuffers(1)

        self._bind()
        self._load_vertices()
        self._load_indices()
        self._unbind()

    def __del__(self) -> None:
        GL.glDeleteBuffers(2, [self._vbo, self._ibo])

    def set_plains(self, plains: List[formations.Plain]) -> None:
        self._plains = plains

        self._bind()
        self._load_vertices()
        self._load_indices()
        self._unbind()

    def render(self) -> None:
        count: Final[int] = 6
        stride: Final[int] = 4 * (3 + 4 + 2)

        self._bind()

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        GL.glVertexAttribPointer(1, 4, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.c_void_p(12))
        GL.glEnableVertexAttribArray(1)

        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.c_void_p(28))
        GL.glEnableVertexAttribArray(2)

        for i, plain in enumerate(self._plains):
            if plain.texture_id is not None:
                GL.glBindTexture(GL.GL_TEXTURE_2D, plain.texture_id)

            GL.glDrawElements(
                    GL.GL_TRIANGLES,
                    count,
                    GL.GL_UNSIGNED_INT,
                    ctypes.c_void_p(4 * count * i),
                )

        GL.glDisableVertexAttribArray(2)
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

    def _load_vertices(self) -> None:
        vertices = self._prepare_vertices()
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL.GL_DYNAMIC_DRAW)

    def _load_indices(self) -> None:
        indices = self._prepare_indices()
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL.GL_STATIC_DRAW)

    def _prepare_vertices(self) -> numpy.array:
        DEFAULT_COLOR = (0.0, 0.0, 0.0, 0.0)

        data = []
        for i, plain in enumerate(self._plains):
            z = 0.5
            x1, x2 = plain.position.x, plain.position.x + plain.size.width
            y1, y2 = plain.position.y, plain.position.y + plain.size.height
            r, g, b, a = plain.color.to_float_tuple() if plain.color is not None else DEFAULT_COLOR

            if plain.flip_vertical:
                t11, t12, t21, t22, t31, t32, t41, t42 = 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0
            else:
                t11, t12, t21, t22, t31, t32, t41, t42 = 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0

            data.append([
                    x1, y1, z, r, g, b, a, t11, t12,
                    x1, y2, z, r, g, b, a, t21, t22,
                    x2, y2, z, r, g, b, a, t31, t32,
                    x2, y1, z, r, g, b, a, t41, t42,
                ])
        return numpy.array(data, dtype=numpy.float32).flatten()

    def _prepare_indices(self) -> numpy.array:
        num_layers = len(self._plains)
        return numpy.array([
                4 * num + offset for num in range(num_layers) for offset in (0, 1, 2, 2, 3, 0)
            ], dtype=numpy.uint32)


class FormationGroup:
    def __init__(self) -> None:
        self._size: Optional[formations.Size] = None
        self._initialized = False
        self._renderer: Optional[PlainRenderer] = None
        self._plains: Optional[List[formations.Plain]] = None

    def set_plains(self, plains: List[formations.Plain]) -> None:
        self._plains = plains
        if self._renderer is not None:
            self._renderer.set_plains(plains)

    def resize(self, width: float, height: float) -> None:
        self._size = formations.Size(width, height)
        self._refresh_view()

    def render(self) -> None:
        if not self._initialized:
            self._initialize()

        if self._is_ready():
            self._setup()
            self._draw()
            self._teardown()

    def _is_ready(self) -> bool:
        return self._size is not None and self._renderer is not None

    def _initialize(self) -> None:
        GL.glClearColor(0.5, 0.5, 0.5, 1)

        self._program = self._load_program('formations')
        self._loc_view = GL.glGetUniformLocation(self._program, "uniView")

        self._renderer = PlainRenderer()
        if self._plains is not None:
            self._renderer.set_plains(self._plains)

        self._initialized = True

    def _load_program(self, id: str) -> int:
        file_template = './shaders/{}_{}.glsl'

        vertex_shader_file = open(file_template.format(id, 'vertex'), 'r')
        vertex_shader_source = vertex_shader_file.read()
        vertex_shader_file.close()

        fragment_shader_file = open(file_template.format(id, 'fragment'), 'r')
        fragment_shader_source = fragment_shader_file.read()
        fragment_shader_file.close()

        vertex_shader = shaders.compileShader(vertex_shader_source, GL.GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(fragment_shader_source, GL.GL_FRAGMENT_SHADER)
        return shaders.compileProgram(vertex_shader, fragment_shader)

    def _refresh_view(self) -> None:
        assert self._size is not None
        left, right, bottom, top = 0, self._size.width, 0, self._size.height
        self._view = geometry.Matrices3D.orthographic(left, right, bottom, top, -100.0, 100.0)

    def _setup(self) -> None:
        assert self._size is not None

        GL.glEnable(GL.GL_TEXTURE_2D)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glViewport(0, 0, self._size.width, self._size.height)

        GL.glClearColor(0.6, 0.6, 0.6, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def _draw(self) -> None:
        assert self._renderer is not None

        GL.glUseProgram(self._program)
        GL.glUniformMatrix4fv(self._loc_view, 1, GL.GL_TRUE, self._view)
        self._renderer.render()
        GL.glUseProgram(0)

    def _teardown(self) -> None:
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_TEXTURE_2D)

