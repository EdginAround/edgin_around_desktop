#!/usr/bin/env python

import ctypes, math, os, sys
import gi, numpy

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk as gtk

from OpenGL import GL
from OpenGL.GL import shaders

from typing import Optional, Tuple

from src import geometry, graphics, media, parsers, skeleton


UI_FILE = "preview.ui"


class GridRenderer:
    def __init__(self) -> None:
        self._vao = GL.glGenVertexArrays(1)
        self._vbo = GL.glGenBuffers(1)

        self._bind()
        self._load_vertices()
        self._unbind()

    def render(self) -> None:
        self._bind()

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

        GL.glDrawArrays(GL.GL_LINES, 0, 4);

        self._unbind()

    def _bind(self) -> None:
        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)

    def _unbind(self) -> None:
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def _load_vertices(self) -> None:
        vertices = numpy.array([-500.0, 0.0, 500.0, 0.0, 0.0, -500.0, 0.0, 500], dtype=numpy.float32)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 4 * 8, vertices, GL.GL_STATIC_DRAW)


class Area(gtk.GLArea):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_auto_render(True)

        self.size: Optional[Tuple[float, float]] = None
        self._initialized = False

        self.add_tick_callback(self.on_clock)

    def on_clock(self, clock, data) -> bool:
        self.queue_render()
        return True

    def do_resize(self, width: float, height: float) -> None:
        self.size = (width, height)
        self.queue_render()

    def do_render(self, ctx) -> bool:
        ctx.make_current()

        if not self._initialized:
            self._initialize()

        if self._is_ready():
            self._setup()
            self._draw()
            self._teardown()

        return True

    def _is_ready(self) -> bool:
        return self.size is not None

    def _initialize(self) -> None:
        GL.glClearColor(0.5, 0.5, 0.5, 1)

        self.program_entity = self._load_program('entities')
        self.loc_entity_view = GL.glGetUniformLocation(self.program_entity, "uniView")
        self.loc_entity_model = GL.glGetUniformLocation(self.program_entity, "uniModel")

        self.program_grid = self._load_program('simple')
        self.loc_grid_view = GL.glGetUniformLocation(self.program_grid, "uniView")

        parser = parsers.SamlParser()
        parser.parse('./res/sprites/pirate/pirate.saml')
        self.skeleton = parser.to_skeleton()
        self.skin = media.Textures(parser.get_images(), dir='./res/sprites/pirate/')

        self.renderer = graphics.SkeletonRenderer(self.skin, self.skeleton)
        self.grid = GridRenderer()

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

    def _setup(self) -> None:
        assert self.size is not None

        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glViewport(0, 0, self.size[0], self.size[1])
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def _draw(self) -> None:
        assert self.size is not None

        view = self._prepare_view()
        model = geometry.Matrices3D.identity()

        GL.glUseProgram(self.program_entity)
        GL.glUniformMatrix4fv(self.loc_entity_view, 1, GL.GL_TRUE, view)
        GL.glUniformMatrix4fv(self.loc_entity_model, 1, GL.GL_TRUE, model)
        self.renderer.render()
        GL.glUseProgram(0)

        GL.glUseProgram(self.program_grid)
        GL.glUniformMatrix4fv(self.loc_grid_view, 1, GL.GL_TRUE, view)
        self.grid.render()
        GL.glUseProgram(0)

    def _teardown(self) -> None:
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_DEPTH_TEST)

    def _prepare_view(self) -> numpy.array:
        assert self.size is not None
        width, height = self.size[0], self.size[1]

        if width < height:
            left, right, bottom, top = -0.5, 0.5, -0.5 * height / width, 0.5 * height / width
        else:
            left, right, bottom, top = -0.5 * width / height, 0.5 * width / height, -0.5, 0.5

        return geometry.Matrices3D.orthographic(left, right, bottom, top, -100.0, 100.0)


class Gui:
    def __init__(self) -> None:
        self.builder = gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)

        area = Area()

        box = self.builder.get_object('box1')
        box.pack_end(area, True, True, 0)

        window = self.builder.get_object('window')
        window.show_all()

    def on_window_destroy(self, window) -> None:
        gtk.main_quit()


if __name__ == "__main__":
    app = Gui()
    sys.exit(gtk.main())

