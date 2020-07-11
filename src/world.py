
import math
import numpy
import pyglet

from OpenGL import GL

from typing import Iterable, List, Optional, Tuple

from . import defs, geometry, graphics, media, scene


class World:
    ZOOM_BOUNDS = (0.0, 1000.0)
    TILT_BOUNDS = (0.0 * math.pi, 0.5 * math.pi)

    def __init__(self, scene: scene.Scene) -> None:
        self.width  = 600
        self.height = 400

        self.highlight_point: Optional[Tuple[float, float]] = None
        self.highlight_actor_id = None

        self.radius = scene.get_radius()
        self.theta = 0.5 * math.pi
        self.phi = 0.0 * math.pi
        self.bearing = 0.0 * math.pi
        self.tilt = 0.4 * math.pi
        self.zoom = 10.0
        self.elevation = 0.0

        self.ready = False
        self.scene = scene
        self.media = media.Media()
        self.media.load_textures()

        self.renderers_entities: List[graphics.PlainRenderer] = list()

    def get_highlight_actor_id(self) -> Optional[defs.ActorId]:
        return self.highlight_actor_id

    def set_lookat(self, position: geometry.Point) -> None:
        self.theta = position.theta
        self.phi = position.phi
        self.elevation = self.scene.get_elevation(position)

    def move(self, right_left, front_back) -> None:
        # Calculate current heading
        transformation = geometry.Matrices.personal_to_global(self.theta, self.phi, self.bearing)
        forward = transformation @ numpy.array((0.0, 0.0, -1.0, 1.0)).reshape(4, 1)
        toward = transformation @ numpy.array((right_left, 0.0, -front_back, 1.0)).reshape(4, 1)

        # Update `theta` and `phi`
        old = geometry.Coordinates.spherical_to_cartesian(self.radius, self.theta, self.phi)
        *new, w = numpy.array((*old, 1.0)).reshape(4, 1) + toward
        r, self.theta, self.phi = geometry.Coordinates.cartesian_to_spherical(*new)

        # Update `elevation`
        self.elevation = self.scene.get_elevation(geometry.Point(self.theta, self.phi))

        # Update `bearing`
        new_forward = numpy.array((*new, 1.0)).reshape(4, 1) + forward
        r, lat1, lon1 = geometry.Coordinates.cartesian_to_geographical_radians(*new)
        r, lat2, lon2 = geometry.Coordinates.cartesian_to_geographical_radians(*new_forward[:3])
        coord1 = geometry.Coordinate(lat1, lon1)
        coord2 = geometry.Coordinate(lat2, lon2)
        self.bearing = coord1.bearing_to(coord2)

    def zoom_by(self, zoom) -> None:
        new_zoom = self.zoom - zoom

        if World.ZOOM_BOUNDS[0] < new_zoom and new_zoom < World.ZOOM_BOUNDS[1]:
            self.zoom = new_zoom

    def rotate_by(self, angle) -> None:
        self.bearing += angle
        while self.bearing > math.pi:
            self.bearing -= 2 * math.pi
        while self.bearing < -math.pi:
            self.bearing += 2 * math.pi

    def tilt_by(self, angle) -> None:
        new_tilt = self.tilt + angle

        if World.TILT_BOUNDS[0] < new_tilt and new_tilt < World.TILT_BOUNDS[1]:
            self.tilt = new_tilt

    def resize(self, width, height) -> None:
        print("Window size: ({}, {})".format(width, height))
        self.width = width
        self.height = height

    def highlight(self, x, y) -> None:
        self.highlight_point = (
                2.0 * x / self.width - 1.0,
                2.0 * y / self.height - 1.0
            )

    def create_renderers(self, actors: Iterable[scene.Actor]) -> None:
        if self.scene.is_ready():
            for actor in actors:
                if actor.position is not None:
                    self.renderers_entities.append(graphics.PlainRenderer(
                        self.scene.get_elevation(actor.position, with_radius=True),
                        actor.position.theta, actor.position.phi, self.bearing,
                        self.media.tex[actor.texture_name],
                        actor.id,
                    ))

    def delete_renderers(self, ids: Iterable[defs.ActorId]) -> None:
        if self.scene.is_ready():
            self.renderers_entities[:] = \
                [render for render in self.renderers_entities if render.actor_id not in ids]

    def draw(self) -> None:
        if not self.ready and self.scene.is_ready():
            self._init_gl()
            self._load_data()
            self.ready = True

        if self.ready:
            self._setup_gl()
            self._draw()
            self._cleanup_gl()

    def _load_shader(self, type, source):
        shader = GL.glCreateShader(type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != 1:
            raise Exception(
                'Couldn\'t compile shader\nShader compilation Log:\n%s\n' %
                GL.glGetShaderInfoLog(shader)
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

        vertex_shader = self._load_shader(GL.GL_VERTEX_SHADER, vertex_shader_source)
        fragment_shader = self._load_shader(GL.GL_FRAGMENT_SHADER, fragment_shader_source)

        program = GL.glCreateProgram()
        GL.glAttachShader(program, vertex_shader)
        GL.glAttachShader(program, fragment_shader)
        GL.glLinkProgram(program)

        return program

    def _init_gl(self):
        self.program_ground = self._load_program('ground_vertex', 'ground_fragment')
        self.program_entities = self._load_program('entities_vertex', 'entities_fragment')

        try:
            GL.glUseProgram(self.program_ground)
            self.loc_ground_proj = GL.glGetUniformLocation(self.program_ground, "uniProj")
            self.loc_ground_view = GL.glGetUniformLocation(self.program_ground, "uniView")
        except OpenGL.error.GLError:
            print(GL.glGetProgramInfoLog(self.program_ground))
            raise

        try:
            GL.glUseProgram(self.program_entities)
            self.loc_entities_proj = GL.glGetUniformLocation(self.program_entities, "uniProj")
            self.loc_entities_view = GL.glGetUniformLocation(self.program_entities, "uniView")
            self.loc_entities_high = GL.glGetUniformLocation(self.program_entities, "uniHighlight")
        except OpenGL.error.GLError:
            print(GL.glGetProgramInfoLog(self.program_entities))
            raise

        GL.glUseProgram(0)

    def _load_data(self) -> None:
        self.radius = self.scene.get_radius()
        self.elevation = self.scene.get_elevation(geometry.Point(self.theta, self.phi))

        figure = geometry.Structures.sphere(5, self.radius)
        self.renderer_water = graphics.SolidPolyhedronRenderer(figure, self.media.tex.water)
        figure.rescale(self.scene.elevation_function)
        self.renderer_ground = graphics.SolidPolyhedronRenderer(figure, self.media.tex.grass)

        self.create_renderers(self.scene.get_actors())

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

    def _setup_gl(self):
        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glViewport(0, 0, self.width, self.height)
        GL.glClearColor(0.6, 0.6, 1.0, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def _cleanup_gl(self):
        GL.glUseProgram(0)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)

        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glDisable(GL.GL_DEPTH_TEST)

    def _draw(self) -> None:
        # Get hero position
        self.set_lookat(self.scene.get_hero_position())

        # Refresh trnasformation
        self._refresh_projection()
        self._refresh_view()

        # Draw ground
        GL.glUseProgram(self.program_ground)
        GL.glUniformMatrix4fv(self.loc_ground_proj, 1, GL.GL_TRUE, self.projection)
        GL.glUniformMatrix4fv(self.loc_ground_view, 1, GL.GL_TRUE, self.view)

        self.renderer_water.render()
        self.renderer_ground.render()

        # Update entities with bearing and sort them by distance from the camera
        mvp = self.projection @ self.view
        for renderer in self.renderers_entities:
            actor = self.scene.get_actor(renderer.actor_id)
            if actor.position is not None:
                renderer.change_position(
                        self.scene.get_elevation(actor.position, with_radius=True),
                        actor.position.theta, actor.position.phi,
                        self.bearing)
                renderer.calculate_screen_bounds(mvp)
        self.renderers_entities.sort(key=graphics.PlainRenderer.get_camera_distance)

        # Find an entity with cursor focus
        highlighted = False
        for renderer in self.renderers_entities:
            highlight = False
            if self.highlight_point is not None and not highlighted:
                highlight = renderer.get_boundary().contains(*self.highlight_point)
                highlighted = highlighted or highlight
                self.highlight_actor_id = renderer.actor_id if highlight else None
            renderer.set_highlight(highlight)

        # Draw entities
        GL.glUseProgram(self.program_entities)
        GL.glUniformMatrix4fv(self.loc_entities_proj, 1, GL.GL_TRUE, self.projection)
        GL.glUniformMatrix4fv(self.loc_entities_view, 1, GL.GL_TRUE, self.view)

        for renderer in self.renderers_entities[::-1]:
            renderer.render(self.loc_entities_high)

