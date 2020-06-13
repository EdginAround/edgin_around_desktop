from OpenGL.GL import *

from . import geometry, graphics

class World:
    ZOOM_BOUNDS = (0.9, 10.1);
    TILT_BOUNDS = (9.0, 81.0);

    def __init__(self):
        self.width  = 600
        self.height = 400
        self.bearing = 0.0
        self.tilt = 40.0
        self.zoom = 10.0
        self.ready = False

    def zoom_by(self, zoom):
        new_zoom = self.zoom - zoom

        if World.ZOOM_BOUNDS[0] < new_zoom and new_zoom < World.ZOOM_BOUNDS[1]:
            self.zoom = new_zoom

            if self.ready:
                self._refresh_view()

    def rotate_by(self, angle):
        self.bearing += angle

        if self.ready:
            self._refresh_view()

    def tilt_by(self, angle):
        new_tilt = self.tilt + angle

        if World.TILT_BOUNDS[0] < new_tilt and new_tilt < World.TILT_BOUNDS[1]:
            self.tilt = new_tilt

            if self.ready:
                self._refresh_view()

    def resize(self, width, height):
        print("Window size: ({}, {})".format(width, height))
        self.width = width
        self.height = height

        if self.ready:
            self._refresh_view()

    def draw(self):
        if not self.ready:
            self._init_gl()
            self._load_data()
            self.ready = True

        self._clear()
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

    def _init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        vertex_shader_file = open('./shaders/vertex.glsl', 'r')
        vertex_shader_source = vertex_shader_file.read()
        vertex_shader_file.close()

        fragment_shader_file = open('./shaders/fragment.glsl', 'r')
        fragment_shader_source = fragment_shader_file.read()
        fragment_shader_file.close()

        vertex_shader = self._load_shader(GL_VERTEX_SHADER, vertex_shader_source)
        fragment_shader = self._load_shader(GL_FRAGMENT_SHADER, fragment_shader_source)

        self.program = glCreateProgram()
        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)

        try:
            glUseProgram(self.program)
            self._refresh_projection()
            self._refresh_view()
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.program))
            raise

    def _load_data(self):
        figure = geometry.Structures.sphere(1)
        self.renderer = graphics.SolidPolyhedronRenderer(figure)

    def _refresh_projection(self):
        projection = geometry.Matrices.projection(45, self.width, self.height, 0.1, 1000.0)
        projectionLocation = glGetUniformLocation(self.program, "uniProj")
        glUniformMatrix4fv(projectionLocation, 1, GL_TRUE, projection)

    def _refresh_view(self):
        view = geometry.Matrices.transposition([0.0, 0.0, -0.1 * self.zoom]) \
             * geometry.Matrices.rotation_x(-1.0 * self.tilt) \
             * geometry.Matrices.transposition([0.0, 0.0, -1.0]) \
             * geometry.Matrices.rotation_z(self.bearing)
        viewLocation = glGetUniformLocation(self.program, "uniView")
        glUniformMatrix4fv(viewLocation, 1, GL_TRUE, view)

    def _clear(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.9, 0.9, 0.9, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def _draw (self):
        self.renderer.render()

