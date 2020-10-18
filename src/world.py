import math
import numpy

from OpenGL import GL

from typing import Dict, Iterable, List, Optional, Tuple

from . import defs, geometry, graphics, media, parsers, scene, skeleton


class World:
    ZOOM_BOUNDS = (0.0, 1000.0)
    TILT_BOUNDS = (0.0 * math.pi, 0.5 * math.pi)

    def __init__(self, scene: scene.Scene) -> None:
        self._width  = 600
        self._height = 400

        self._highlight_point: Optional[Tuple[float, float]] = None
        self._highlight_actor_id: Optional[defs.ActorId] = None

        self._radius = scene.get_radius()
        self._theta = 0.5 * math.pi
        self._phi = 0.0 * math.pi
        self._bearing = 0.0 * math.pi
        self._tilt = 0.4 * math.pi
        self._zoom = 10.0
        self._elevation = 0.0

        self._ready = False
        self._scene = scene
        self._media = media.Media()
        self._media.load_tiles()

        self._skeletons: Dict[defs.ActorId, skeleton.Skeleton] = dict()
        self._renderers_entities: List[graphics.PositionedSkeletonRenderer] = list()

    def get_theta(self) -> float:
        return self._theta

    def get_phi(self) -> float:
        return self._phi

    def get_bearing(self) -> float:
        return self._bearing

    def get_highlight_actor_id(self) -> Optional[defs.ActorId]:
        return self._highlight_actor_id

    def move(self, right_left, front_back) -> None:
        # Calculate current heading
        transformation = geometry.Matrices3D.personal_to_global(self._theta, self._phi, self._bearing)
        forward = transformation @ numpy.array((0.0, 0.0, -1.0, 1.0)).reshape(4, 1)
        toward = transformation @ numpy.array((right_left, 0.0, -front_back, 1.0)).reshape(4, 1)

        # Update `theta` and `phi`
        old = geometry.Coordinates.spherical_to_cartesian(self._radius, self._theta, self._phi)
        *new, w = numpy.array((*old, 1.0)).reshape(4, 1) + toward
        r, self._theta, self._phi = geometry.Coordinates.cartesian_to_spherical(*new)

        # Update `elevation`
        self._elevation = self._scene.get_elevation(geometry.Point(self._theta, self._phi))

        # Update `bearing`
        new_forward = numpy.array((*new, 1.0)).reshape(4, 1) + forward
        r, lat1, lon1 = geometry.Coordinates.cartesian_to_geographical_radians(*new)
        r, lat2, lon2 = geometry.Coordinates.cartesian_to_geographical_radians(*new_forward[:3])
        coord1 = geometry.Coordinate(lat1, lon1)
        coord2 = geometry.Coordinate(lat2, lon2)
        self._bearing = coord1.bearing_to(coord2)

    def zoom_by(self, zoom) -> None:
        new_zoom = self._zoom - zoom

        if World.ZOOM_BOUNDS[0] < new_zoom and new_zoom < World.ZOOM_BOUNDS[1]:
            self. _zoom = new_zoom

    def rotate_by(self, angle) -> None:
        self._bearing += angle
        while self._bearing > math.pi:
            self._bearing -= 2 * math.pi
        while self._bearing < -math.pi:
            self._bearing += 2 * math.pi

    def tilt_by(self, angle) -> None:
        new_tilt = self._tilt + angle

        if World.TILT_BOUNDS[0] < new_tilt and new_tilt < World.TILT_BOUNDS[1]:
            self._tilt = new_tilt

    def resize(self, width, height) -> None:
        print("Window size: ({}, {})".format(width, height))
        self._width = width
        self._height = height

    def highlight(self, x, y) -> None:
        self._highlight_point = (
                2.0 * x / self._width - 1.0,
                2.0 * y / self._height - 1.0
            )

    def create_renderers(self, actors: Iterable[scene.Actor]) -> None:
        if not self._scene.is_ready():
            return

        for actor in actors:
            skeleton = self._load_skeleton_and_skin(actor.entity_name)

            self._skeletons[actor.id] = skeleton

            if actor.position is not None:
                self._renderers_entities.append(graphics.PositionedSkeletonRenderer(
                    skeleton,
                    self._scene.get_elevation(actor.position, with_radius=True),
                    actor.position.theta, actor.position.phi, self._bearing,
                    actor.id,
                    geometry.Matrices3D.identity(),
                ))

    def delete_renderers(self, ids: Iterable[defs.ActorId]) -> None:
        if not self._scene.is_ready():
            return

        self._skeletons = \
            {id: skeleton for id, skeleton in self._skeletons.items() if id not in ids}
        self._renderers_entities[:] = \
            [render for render in self._renderers_entities if render.get_actor_id() not in ids]

    def play_animation(self, actor_id: defs.ActorId, animation_name: str):
        renderer = self._find_renderer(actor_id)
        if renderer is None:
            return

        renderer.select_animation(animation_name)

    def attach_skeleton(
            self,
            target_id: defs.ActorId,
            source_id: Optional[defs.ActorId],
            attachment: defs.Attachement,
        ) -> None:
        target_renderer = self._find_renderer(target_id)
        if target_renderer is None:
            return

        source_skeleton = None
        if source_id is not None:
            source_skeleton = self._find_skeleton(source_id)
            if source_skeleton is not None:
                source_skeleton.select_animation('held')

        target_renderer.attach_skeleton(attachment.value, source_skeleton)

    def draw(self) -> None:
        if not self._ready and self._scene.is_ready():
            self._init_gl()
            self._load_data()
            self._ready = True

        if self._ready:
            self._setup_gl()
            self._draw()
            self._cleanup_gl()

    def _find_skeleton(self, actor_id: defs.ActorId) -> Optional[skeleton.Skeleton]:
        return self._skeletons.get(actor_id, None)

    def _find_renderer(
            self,
            actor_id: defs.ActorId,
        ) -> Optional[graphics.PositionedSkeletonRenderer]:
        for renderer in self._renderers_entities:
            if renderer.get_actor_id() == actor_id:
                return renderer
        return None

    def _set_lookat(self, position: geometry.Point) -> None:
        self._theta = position.theta
        self._phi = position.phi
        self._elevation = self._scene.get_elevation(position)

    def _load_shader(self, type, source) -> int:
        shader = GL.glCreateShader(type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != 1:
            raise Exception(
                'Couldn\'t compile shader\nShader compilation Log:\n%s\n' %
                GL.glGetShaderInfoLog(shader)
            )

        return shader

    def _load_program(self, vertex, fragment) -> int:
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

    def _load_skeleton_and_skin(self, name: str) -> skeleton.Skeleton:
        dirpath = f'{media.DIR_SPRITES}/{name}'
        filepath = f'{dirpath}/{name}.saml'
        parser = parsers.SamlParser()
        parser.parse(filepath)
        skeleton = parser.to_skeleton(name)
        self._media.load_skin(name)
        return skeleton

    def _init_gl(self) -> None:
        self._program_ground = self._load_program('ground_vertex', 'ground_fragment')
        self._program_entities = self._load_program('entities_vertex', 'entities_fragment')

        try:
            GL.glUseProgram(self._program_ground)
            self._loc_ground_view = GL.glGetUniformLocation(self._program_ground, "uniView")
        except GL.error.GLError:
            print(GL.glGetProgramInfoLog(self._program_ground))
            raise

        try:
            GL.glUseProgram(self._program_entities)
            self._loc_entities_view = GL.glGetUniformLocation(self._program_entities, "uniView")
            self._loc_entities_model = GL.glGetUniformLocation(self._program_entities, "uniModel")
            self._loc_entities_highlight = \
                    GL.glGetUniformLocation(self._program_entities, "uniHighlight")
        except GL.error.GLError:
            print(GL.glGetProgramInfoLog(self._program_entities))
            raise

        GL.glUseProgram(0)

    def _load_data(self) -> None:
        def rescale(point: geometry.Point):
            assert self._scene.elevation_function is not None
            return self._scene.elevation_function.evaluate_with_radius(point)

        self._radius = self._scene.get_radius()
        self._elevation = self._scene.get_elevation(geometry.Point(self._theta, self._phi))

        figure = geometry.Structures.sphere(5, self._radius)
        self._renderer_water = graphics.SolidPolyhedronRenderer(figure, self._media.tex.water)
        figure.rescale(rescale)
        self._renderer_ground = graphics.SolidPolyhedronRenderer(figure, self._media.tex.grass)

    def _refresh_view(self) -> None:
        self._view = \
            geometry.Matrices3D.perspective(0.25 * math.pi, self._width, self._height, 1.0, 100.0) @\
            geometry.Matrices3D.translation((0.0, 0.0, -self._zoom)) @ \
            geometry.Matrices3D.rotation_x(-self._tilt) @ \
            geometry.Matrices3D.translation((0.0, 0.0, -(self._radius + self._elevation))) @ \
            geometry.Matrices3D.rotation_z(self._bearing) @ \
            geometry.Matrices3D.rotation_x(-self._theta) @ \
            geometry.Matrices3D.rotation_z(-self._phi) @ \
            geometry.Matrices3D.rotation_x(0.5 * math.pi)

    def _setup_gl(self) -> None:
        GL.glUseProgram(0)

        GL.glEnable(GL.GL_BLEND)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glViewport(0, 0, self._width, self._height)
        GL.glClearColor(0.6, 0.6, 1.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def _cleanup_gl(self) -> None:
        GL.glUseProgram(0)

        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glDisable(GL.GL_DEPTH_TEST)

    def _draw(self) -> None:
        # Get hero position
        self._set_lookat(self._scene.get_hero_position())

        # Refresh transformation
        self._refresh_view()

        # Draw ground
        GL.glUseProgram(self._program_ground)
        GL.glUniformMatrix4fv(self._loc_ground_view, 1, GL.GL_TRUE, self._view)

        self._renderer_water.render()
        self._renderer_ground.render()

        # Update entities with bearing and sort them by distance from the camera
        for renderer in self._renderers_entities:
            actor = self._scene.get_actor(renderer.get_actor_id())
            renderer.set_visibility(actor.is_visible())
            if actor.position is not None:
                renderer.change_position_and_view(
                        self._scene.get_elevation(actor.position, with_radius=True),
                        actor.position.theta, actor.position.phi,
                        self._bearing, self._view)
        self._renderers_entities.sort(key=graphics.PositionedSkeletonRenderer.get_camera_distance)

        # Find an entity with cursor focus
        highlighted = False
        for renderer in self._renderers_entities:
            if renderer.is_visible():
                highlight = False
                if self._highlight_point is not None and not highlighted:
                    highlight = renderer.reacts_to(*self._highlight_point)
                    highlighted = highlighted or highlight
                    self._highlight_actor_id = renderer.get_actor_id() if highlight else None
                renderer.set_highlight(highlight)

        # Draw entities
        GL.glUseProgram(self._program_entities)
        GL.glUniformMatrix4fv(self._loc_entities_view, 1, GL.GL_TRUE, self._view)

        for renderer in self._renderers_entities[::-1]:
            if renderer.is_visible():
                renderer.render(
                    self._loc_entities_highlight,
                    self._loc_entities_model,
                    self._media.skins,
                )

