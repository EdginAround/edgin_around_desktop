import numpy
import pyglet

from OpenGL.GL import *

from . import geometry, graphics

class World:
    ZOOM_BOUNDS = (29.0, 121.0);
    TILT_BOUNDS = (9.0, 81.0);

    def __init__(self, radius):
        self.radius = radius
        self.width  = 600
        self.height = 400
        self.bearing = 0.0
        self.tilt = 40.0
        self.zoom = 90.0
        self.highlight_point = None
        self.ready = False

    def zoom_by(self, zoom):
        new_zoom = self.zoom - zoom

        if World.ZOOM_BOUNDS[0] < new_zoom and new_zoom < World.ZOOM_BOUNDS[1]:
            self.zoom = new_zoom

    def rotate_by(self, angle):
        self.bearing += angle

    def tilt_by(self, angle):
        new_tilt = self.tilt + angle

        if World.TILT_BOUNDS[0] < new_tilt and new_tilt < World.TILT_BOUNDS[1]:
            self.tilt = new_tilt

    def resize(self, width, height):
        print("Window size: ({}, {})".format(width, height))
        self.width = width
        self.height = height

    def highlight(self, x, y):
        self.highlight_point = (
                2.0 * x / self.width - 1.0,
                2.0 * y / self.height - 1.0
            )

    def draw(self):
        if not self.ready:
            self._init_gl()
            self._load_data()
            self.ready = True

        self._draw()

    def _load_shader(self, type, source):
        shader = glCreateShader(type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if glGetShaderiv(shader,GL_COMPILE_STATUS) != 1:
            raise Exception(
                'Couldn\'t compile shader\nShader compilation Log:\n%s\n' %
                glGetShaderInfoLog(shader)
            )

        return shader

    def _load_program(self, vertex, fragment):
        file_template = './shaders/{}.glsl'

        vertex_shader_file = open(file_template.format(vertex), 'r')
        vertex_shader_source = vertex_shader_file.read()
        vertex_shader_file.close()

        fragment_shader_file = open(file_template.format(fragment), 'r')
        fragment_shader_source = fragment_shader_file.read()
        fragment_shader_file.close()

        vertex_shader = self._load_shader(GL_VERTEX_SHADER, vertex_shader_source)
        fragment_shader = self._load_shader(GL_FRAGMENT_SHADER, fragment_shader_source)

        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)

        return program

    def _init_gl(self):
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.ground_program = self._load_program('ground_vertex', 'ground_fragment')
        self.entities_program = self._load_program('entities_vertex', 'entities_fragment')

        try:
            glUseProgram(self.ground_program)
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.ground_program))
            raise

        try:
            glUseProgram(self.entities_program)
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.entities_program))
            raise

    def _load_data(self):
        figure = geometry.Structures.sphere(4, self.radius)
        self.ground_renderer = graphics.SolidPolyhedronRenderer(figure)

        self.renderers = (
                graphics.PlainRenderer((0.0, 0.0, 100.0)),
                graphics.PlainRenderer((1.0, 1.0, 100.0))
            )

        image = pyglet.image.load("images/grass.png")
        self.grass_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.grass_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.get_data()
        )

        image = pyglet.image.load("images/hero.png")
        self.hero_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.hero_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.get_data()
        )

    def _refresh_projection(self):
        self.projection = geometry.Matrices.projection(45, self.width, self.height, 0.1, 1000.0)

    def _refresh_view(self):
        self.view = geometry.Matrices.transposition([0.0, 0.0, -0.1 * self.zoom]) \
                  * geometry.Matrices.rotation_x(-1.0 * self.tilt) \
                  * geometry.Matrices.transposition([0.0, 0.0, -1.0 * self.radius]) \
                  * geometry.Matrices.rotation_z(self.bearing)

    def _draw (self):
        # Set up
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.6, 0.6, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw ground
        glClear(GL_DEPTH_BUFFER_BIT)
        glBindTexture(GL_TEXTURE_2D, self.grass_tex)
        glUseProgram(self.ground_program)
        self._refresh_projection()
        self._refresh_view()
        projection_location = glGetUniformLocation(self.ground_program, "uniProj")
        glUniformMatrix4fv(projection_location, 1, GL_TRUE, self.projection)
        view_location = glGetUniformLocation(self.ground_program, "uniView")
        glUniformMatrix4fv(view_location, 1, GL_TRUE, self.view)

        self.ground_renderer.render()

        # Find an entity with cursor focus
        index = None
        if self.highlight_point is not None:
            mvp = self.projection * self.view
            offset1 = numpy.array((-0.5, 0.0, 0.0, 0.0)).reshape(4, 1)
            offset2 = numpy.array(( 0.5, 0.0, 1.0, 0.0)).reshape(4, 1)
            for i, renderer in enumerate(self.renderers):
                anchor = numpy.array((*renderer.pos, 1.0)).reshape(4, 1)
                vertex1, vertex2 = mvp * (anchor + offset1), mvp * (anchor + offset2)
                vertex1, vertex2 = vertex1 / vertex1[3], vertex2 / vertex2[3]
                left, bottom, right, top = vertex1[0], vertex1[1], vertex2[0], vertex2[1]
                nx, ny = self.highlight_point[0], self.highlight_point[1]
                if left < nx and nx < right and bottom < ny and ny < top:
                    index = len(self.renderers) - i - 1
                    break

        # Draw entities
        glBindTexture(GL_TEXTURE_2D, self.hero_tex)
        glUseProgram(self.entities_program)
        self._refresh_projection()
        self._refresh_view()
        projection_location = glGetUniformLocation(self.entities_program, "uniProj")
        glUniformMatrix4fv(projection_location, 1, GL_TRUE, self.projection)
        view_location = glGetUniformLocation(self.entities_program, "uniView")
        glUniformMatrix4fv(view_location, 1, GL_TRUE, self.view)

        for i, renderer in enumerate(self.renderers[::-1]):
            glClear(GL_DEPTH_BUFFER_BIT)
            highlight_location = glGetUniformLocation(self.entities_program, "uniHighlight")
            glUniform1i(highlight_location, int(i == index))
            renderer.render()

        # Clean up
        glUseProgram(0)

