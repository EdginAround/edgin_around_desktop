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

        self.program_ground = self._load_program('ground_vertex', 'ground_fragment')
        self.program_entities = self._load_program('entities_vertex', 'entities_fragment')

        try:
            glUseProgram(self.program_ground)
            self.loc_ground_proj = glGetUniformLocation(self.program_ground, "uniProj")
            self.loc_ground_view = glGetUniformLocation(self.program_ground, "uniView")
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.program_ground))
            raise

        try:
            glUseProgram(self.program_entities)
            self.loc_entities_proj = glGetUniformLocation(self.program_entities, "uniProj")
            self.loc_entities_view = glGetUniformLocation(self.program_entities, "uniView")
            self.loc_entities_high = glGetUniformLocation(self.program_entities, "uniHighlight")
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.program_entities))
            raise

    def _load_texture(self, image_path):
        image = pyglet.image.load(image_path)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.get_data()
        )
        return texture

    def _load_data(self):
        self.tex_grass = self._load_texture("res/images/grass.png")
        self.tex_water = self._load_texture("res/images/water.png")
        self.tex_hero = self._load_texture("res/images/hero.png")

        figure = geometry.Structures.sphere(5, self.radius)
        self.renderer_water = graphics.SolidPolyhedronRenderer(figure, self.tex_water)
        figure.rescale(self.state.elevation_function)
        self.renderer_ground = graphics.SolidPolyhedronRenderer(figure, self.tex_grass)

        self.renderer_hero = graphics.PlainRenderer(
                self.radius + self.elevation,
                self.theta, self.phi, self.bearing,
                self.tex_hero
            )

        self.renderers_entities = [graphics.PlainRenderer(
            self.state.elevation_function(self.theta, self.phi),
            *coord, self.bearing, self.tex_hero
        ) for coord in (
            (0.499 * math.pi, 0.001 * math.pi),
            (0.498 * math.pi, 0.002 * math.pi),
        )]

    def _refresh_projection(self):
        self.projection = \
            geometry.Matrices.projection(0.25 * math.pi, self.width, self.height, 0.1, 1000.0)

    def _refresh_view(self):
        self.view = geometry.Matrices.translation([0.0, 0.0, -self.zoom]) \
                  @ geometry.Matrices.rotation_x(-self.tilt) \
                  @ geometry.Matrices.translation([0.0, 0.0, -(self.radius + self.elevation)]) \
                  @ geometry.Matrices.rotation_z(self.bearing) \
                  @ geometry.Matrices.rotation_x(-self.theta) \
                  @ geometry.Matrices.rotation_z(-self.phi) \
                  @ geometry.Matrices.rotation_x(0.5 * math.pi)

    def _draw(self):
        # Set up
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.6, 0.6, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._refresh_projection()
        self._refresh_view()

        # Draw ground
        glUseProgram(self.program_ground)
        glUniformMatrix4fv(self.loc_ground_proj, 1, GL_TRUE, self.projection)
        glUniformMatrix4fv(self.loc_ground_view, 1, GL_TRUE, self.view)

        self.renderer_water.render()
        self.renderer_ground.render()

        # Update entities with bearing and sort them by distance from the camera
        mvp = self.projection @ self.view
        for renderer in self.renderers_entities:
            renderer.change_bearing(self.bearing)
            renderer.calculate_screen_bounds(mvp)
        self.renderers_entities.sort(key=graphics.PlainRenderer.get_camera_distance)

        # Find an entity with cursor focus
        highlighted = False
        for renderer in self.renderers_entities:
            highlight = False
            if self.highlight_point is not None and not highlighted:
                highlight = renderer.get_boundary().contains(*self.highlight_point)
                highlighted = highlighted or highlight
            renderer.set_highlight(highlight)

        # Draw entities
        glUseProgram(self.program_entities)
        glUniformMatrix4fv(self.loc_entities_proj, 1, GL_TRUE, self.projection)
        glUniformMatrix4fv(self.loc_entities_view, 1, GL_TRUE, self.view)

        for renderer in self.renderers_entities[::-1]:
            renderer.render(self.loc_entities_high)

        glUniform1i(self.loc_entities_high, False)
        self.renderer_hero \
            .change_position(self.radius + self.elevation, self.theta, self.phi, self.bearing)
        self.renderer_hero.render(self.loc_entities_high)

        # Clean up
        glUseProgram(0)

