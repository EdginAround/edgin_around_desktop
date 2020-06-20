import math
import numpy
import pyglet

from OpenGL.GL import *

from . import geometry, graphics

class World:
    ZOOM_BOUNDS = (0.0, 1000.0)
    TILT_BOUNDS = (0.0 * math.pi, 0.5 * math.pi)

    def __init__(self, state):
        self.width  = 600
        self.height = 400
        self.highlight_point = None

        self.radius = state.get_radius()
        self.theta = 0.5 * math.pi
        self.phi = 0.0 * math.pi
        self.bearing = 0.0 * math.pi
        self.tilt = 0.4 * math.pi
        self.zoom = 10.0
        self.elevation = state.elevation_function(self.theta, self.phi) - self.radius

        self.ready = False
        self.state = state

    def set_lookat(self, theta, phi):
        self.theta = theta
        self.phi = phi
        self.elevation = self.state.elevation_function(theta, phi) - self.radius

    def move(self, right_left, front_back):
        # Calculate current heading
        transformation = geometry.Matrices.personal_to_global(self.theta, self.phi, self.bearing)
        forward = transformation @ numpy.array((0.0, 0.0, -1.0, 1.0)).reshape(4, 1)
        toward = transformation @ numpy.array((right_left, 0.0, -front_back, 1.0)).reshape(4, 1)

        # Update `theta` and `phi`
        old = geometry.Coordinates.spherical_to_cartesian(self.radius, self.theta, self.phi)
        *new, w = numpy.array((*old, 1.0)).reshape(4, 1) + toward
        r, self.theta, self.phi = geometry.Coordinates.cartesian_to_spherical(*new)

        # Update `elevation`
        self.elevation = self.state.elevation_function(self.theta, self.phi) - self.radius

        # Update `bearing`
        new_forward = numpy.array((*new, 1.0)).reshape(4, 1) + forward
        r, lat1, lon1 = geometry.Coordinates.cartesian_to_geographical_radians(*new)
        r, lat2, lon2 = geometry.Coordinates.cartesian_to_geographical_radians(*new_forward[:3])
        self.bearing = geometry.bearing_geographical(lat1, lon1, lat2, lon2)

    def zoom_by(self, zoom):
        new_zoom = self.zoom - zoom

        if World.ZOOM_BOUNDS[0] < new_zoom and new_zoom < World.ZOOM_BOUNDS[1]:
            self.zoom = new_zoom

    def rotate_by(self, angle):
        self.bearing += angle
        while self.bearing > math.pi:
            self.bearing -= 2 * math.pi
        while self.bearing < -math.pi:
            self.bearing += 2 * math.pi

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
        figure = geometry.Structures.sphere(5, self.radius)
        self.water_renderer = graphics.SolidPolyhedronRenderer(figure)
        figure.rescale(self.state.elevation_function)
        self.ground_renderer = graphics.SolidPolyhedronRenderer(figure)

        coordinates = (
            (0.500 * math.pi, 0.000 * math.pi),
            (0.499 * math.pi, 0.001 * math.pi),
            (0.498 * math.pi, 0.002 * math.pi),
        )

        self.renderers = [graphics.PlainRenderer(
            geometry.Coordinates.spherical_to_cartesian(
                self.state.elevation_function(*coord), *coord
            )
        ) for coord in coordinates]

        image = pyglet.image.load("res/images/grass.png")
        self.grass_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.grass_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.get_data()
        )

        image = pyglet.image.load("res/images/water.png")
        self.water_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.water_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.get_data()
        )

        image = pyglet.image.load("res/images/hero.png")
        self.hero_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.hero_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.get_data()
        )

    def _refresh_projection(self):
        self.projection = \
            geometry.Matrices.projection(0.25 * math.pi, self.width, self.height, 0.1, 1000.0)

    def _refresh_view(self):
        self.view = geometry.Matrices.transposition([0.0, 0.0, -self.zoom]) \
                  @ geometry.Matrices.rotation_x(-self.tilt) \
                  @ geometry.Matrices.transposition([0.0, 0.0, -(self.radius + self.elevation)]) \
                  @ geometry.Matrices.rotation_z(-self.bearing) \
                  @ geometry.Matrices.rotation_x(self.theta) \
                  @ geometry.Matrices.rotation_z(self.phi) \
                  @ geometry.Matrices.rotation_x(-0.5 * math.pi)

    def _draw(self):
        # Set up
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.6, 0.6, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        self._refresh_projection()
        self._refresh_view()

        # Draw ground
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.ground_program)
        projection_location = glGetUniformLocation(self.ground_program, "uniProj")
        glUniformMatrix4fv(projection_location, 1, GL_TRUE, self.projection)
        view_location = glGetUniformLocation(self.ground_program, "uniView")
        glUniformMatrix4fv(view_location, 1, GL_TRUE, self.view)

        glBindTexture(GL_TEXTURE_2D, self.water_tex)
        self.water_renderer.render()

        glBindTexture(GL_TEXTURE_2D, self.grass_tex)
        self.ground_renderer.render()

        # Find an entity with cursor focus
        index = None
        if self.highlight_point is not None:
            mvp = self.projection @ self.view
            offset1 = numpy.array((-0.5, 0.0, 0.0, 0.0)).reshape(4, 1)
            offset2 = numpy.array(( 0.5, 0.0, 1.0, 0.0)).reshape(4, 1)
            for i, renderer in enumerate(self.renderers):
                anchor = numpy.array((*renderer.pos, 1.0)).reshape(4, 1)
                vertex1, vertex2 = mvp @ (anchor + offset1), mvp @ (anchor + offset2)
                vertex1, vertex2 = vertex1 / vertex1[3], vertex2 / vertex2[3]
                left, bottom, right, top = vertex1[0], vertex1[1], vertex2[0], vertex2[1]
                nx, ny = self.highlight_point[0], self.highlight_point[1]
                if left < nx and nx < right and bottom < ny and ny < top:
                    index = len(self.renderers) - i - 1
                    break

        # Draw entities
        glBindTexture(GL_TEXTURE_2D, self.hero_tex)
        glUseProgram(self.entities_program)
        projection_location = glGetUniformLocation(self.entities_program, "uniProj")
        glUniformMatrix4fv(projection_location, 1, GL_TRUE, self.projection)
        view_location = glGetUniformLocation(self.entities_program, "uniView")
        glUniformMatrix4fv(view_location, 1, GL_TRUE, self.view)

        for i, renderer in enumerate(self.renderers[::-1]):
            #glClear(GL_DEPTH_BUFFER_BIT)
            highlight_location = glGetUniformLocation(self.entities_program, "uniHighlight")
            glUniform1i(highlight_location, int(i == index))
            renderer.render()

        # Clean up
        glUseProgram(0)

