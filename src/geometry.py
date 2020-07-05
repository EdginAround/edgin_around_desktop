import numpy

from math import asin, atan2, cos, degrees, pi, radians, sin, sqrt, tan

####################################################################################################

class Polyhedron:
    """"Polyhedron data container."""

    def __init__(self, vertices, triangles, colors=None):
        # An ordered list of points.
        self.vertices = list(vertices)

        # A set of triangles defined as tuples of indices.
        self.triangles = {tuple(sorted(point)) for point in triangles}

        # An ordered list of colors.
        self.colors = colors

    def get_vertices(self):
        for vertex in self.vertices:
            yield vertex

    def get_triangles(self):
        for triangle in self.triangles:
            yield triangle

    def get_vertex(self, index):
        return self.vertices[index], self.colors[index]

    def rescale(self, stretch):
        for i, vertex in enumerate(self.vertices):
            r, theta, phi = Coordinates.cartesian_to_spherical(*vertex)
            multiplier = stretch(theta, phi) / r
            self.vertices[i] = [v * multiplier for v in vertex]

####################################################################################################

class Structures:
    """Structures generator class."""

    @staticmethod
    def icosahedron():
        """Icosahedron generation function"""

        f = (sqrt(5.0) + 1.0) / 2.0
        b = sqrt(2.0 / (5.0 + sqrt(5.0)))
        a = b * f

        return Polyhedron(
                 (( 0, b, a), ( 0, b,-a), ( 0,-b, a), ( 0,-b,-a),
                  ( a, 0, b), ( a, 0,-b), (-a, 0, b), (-a, 0,-b),
                  ( b, a, 0), ( b,-a, 0), (-b, a, 0), (-b,-a, 0)),
             set(((0,  2, 4), (0,  2, 6), (1,  3,  5), (1,  3,  7),
                  (4,  5, 8), (4,  5, 9), (6,  7, 10), (6,  7, 11),
                  (8, 10, 0), (8, 10, 1), (9, 11,  2), (9, 11,  3),
                  (4,  8, 0), (5,  8, 1), (4,  9,  2), (5,  9,  3),
                  (6, 10, 0), (7, 10, 1), (6, 11,  2), (7, 11,  3)))
            )

    @staticmethod
    def sphere(n, radius=1.0):
        """Sphere generation function"""

        def scaled(vector):
            length_inv = 1.0 / sqrt(sum(v*v for v in vector))
            return tuple([radius * v * length_inv for v in vector])

        def nm(v1, v2):
            return scaled([0.5 * (v1[i] + v2[i]) for i in range(0, len(v1))])

        def index(v):
            if v not in indices:
                indices[v] = len(vertices)
                vertices.append(v)

            return indices[v]

        icosahedron = Structures.icosahedron()
        vertices = [scaled(v) for v in icosahedron.vertices]
        old_triangles = icosahedron.triangles
        indices = {v: i for i, v in enumerate(vertices)}

        for i in range(0, n):
            new_triangles = set()

            for t in old_triangles:
                v0 = nm(vertices[t[1]], vertices[t[2]])
                v1 = nm(vertices[t[0]], vertices[t[2]])
                v2 = nm(vertices[t[0]], vertices[t[1]])

                p0 = index(v0)
                p1 = index(v1)
                p2 = index(v2)

                new_triangles.update([(t[0], p1, p2)])
                new_triangles.update([(t[1], p0, p2)])
                new_triangles.update([(t[2], p0, p1)])
                new_triangles.update([(p0, p1, p2)])

            old_triangles = new_triangles

        return Polyhedron(vertices, new_triangles)

####################################################################################################

class Matrices:
    """Matrix generator class."""

    @staticmethod
    def projection(fovy, width, height, near, far):
        s = 1.0 / tan(0.5 * fovy)
        sx, sy = s * height / width, s
        zz = (far + near) / (near - far)
        zw = 2 * far * near / (near - far)
        return numpy.array([
            [sx,  0,  0,  0],
            [ 0, sy,  0,  0],
            [ 0,  0, zz, zw],
            [ 0,  0, -1,  0]
        ], dtype = numpy.float32)

    @staticmethod
    def translation(vector):
        x, y, z = vector[0], vector[1], vector[2]
        return numpy.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_x(a):
        c, s = cos(a), sin(a)
        return numpy.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0,   c,  -s, 0.0],
            [0.0,   s,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_y(a):
        c, s = cos(a), sin(a)
        return numpy.array([
            [  c, 0.0,   s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [ -s, 0.0,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_z(a):
        c, s = cos(a), sin(a)
        return numpy.array([
            [  c,  -s, 0.0, 0.0],
            [  s,   c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def personal_to_global(theta, phi, bearing):
        return Matrices.rotation_y(phi) \
             @ Matrices.rotation_x(theta) \
             @ Matrices.rotation_y(-bearing)

####################################################################################################

class Coordinates:
    @staticmethod
    def cartesian_to_spherical(x, y, z):
        r = sqrt(x * x + y * y + z * z)
        theta = atan2(sqrt(x * x + z * z), y) if y != 0.0 else 0.5 * pi
        phi = atan2(x, z) if z != 0.0 else 0.5 * pi
        return r, theta, phi

    @staticmethod
    def cartesian_to_geographical_radians(x, y, z):
        coords = Coordinates.cartesian_to_spherical(x, y, z)
        return Coordinates.spherical_to_geographical_radians(*coords)

    @staticmethod
    def cartesian_to_geographical_degrees(x, y, z):
        coords = Coordinates.cartesian_to_spherical(x, y, z)
        return Coordinates.spherical_to_geographical_degrees(*coords)

    @staticmethod
    def spherical_to_cartesian(r, theta, phi):
        z = r * sin(theta) * cos(phi)
        x = r * sin(theta) * sin(phi)
        y = r * cos(theta)
        return x, y, z

    @staticmethod
    def spherical_to_geographical_radians(r, theta, phi):
        lat = 0.5 * pi - theta
        lon = phi if phi <= pi else phi - 2.0 * pi
        return r, lat, lon

    @staticmethod
    def spherical_to_geographical_degrees(r, theta, phi):
        r, lat, lon = Coordinates.spherical_to_geographical_radians(r, theta, phi)
        return r, degrees(lat), degrees(lon)

    @staticmethod
    def geographical_radians_to_spherical(r, lat, lon):
        theta = 0.5 * pi - lat
        phi = lon if lon >= 0 else lon + 2.0 * pi
        return r, theta, phi

    @staticmethod
    def geographical_degrees_to_spherical(r, lat, lon):
        return Coordinates.geographical_radians_to_spherical(r, radians(lat), radians(lon))

####################################################################################################

class Coordinate:
    """Position expressed in geographical coordinates with radians."""

    def __init__(self, lat, lon) -> None:
        self.lat = lat
        self.lon = lon

    def bearing_to(self, other: 'Coordinate') -> float:
        """Calculates bearing between two coordinates."""

        x = sin(other.lon - self.lon) * cos(other.lat)
        y = cos(self.lat) * sin(other.lat) - \
            sin(self.lat) * cos(other.lat) * cos(other.lon - self.lon)

        return atan2(x, y)

    def great_circle_distance_to(self, other: 'Coordinate', radius: float) -> float:
        sin1 = sin(0.5 * abs(self.lat - other.lat))
        sin2 = sin(0.5 * abs(self.lon - other.lon))
        return 2 * radius * asin(sqrt(sin1 * sin1 + cos(self.lat) * cos(other.lat) * sin2 * sin2))

    def moved_by(self, distance, bearing, radius) -> 'Coordinate':
        angular_distance = distance / radius
        cad = cos(angular_distance)
        sad = sin(angular_distance)

        cb = cos(bearing)
        sb = sin(bearing)

        slat1 = sin(self.lat)
        clat1 = cos(self.lat)

        lat2 = asin(slat1 * cad + clat1 * sad * cb)
        slat2 = sin(lat2)
        lon2 = self.lon + atan2(sb * sad * clat1, cad - slat1 * slat2)

        return Coordinate(lat2, lon2)

    def to_point(self) -> 'Point':
        r, theta, phi = Coordinates.geographical_radians_to_spherical(1.0, self.lat, self.lon)
        return Point(theta, phi)

####################################################################################################

class Point:
    """Position expressed in spherical coordinates."""

    def __init__(self, theta, phi) -> None:
        self.theta = theta
        self.phi = phi

    def bearing_to(self, other: 'Point') -> float:
        """Calculates bearing between two points expressed in spherical coordinates."""

        coord1 = self.to_coordinate()
        coord2 = other.to_coordinate()
        return coord1.bearing_to(coord2)

    def great_circle_distance_to(self, other: 'Point', radius: float) -> float:
        coord1 = self.to_coordinate()
        coord2 = other.to_coordinate()
        return coord1.great_circle_distance_to(coord2, radius)

    def moved_by(self, distance, bearing, radius) -> 'Point':
        return self.to_coordinate().moved_by(distance, bearing, radius).to_point()

    def to_coordinate(self) -> Coordinate:
        r, lat, lon = Coordinates.spherical_to_geographical_radians(1.0, self.theta, self.phi)
        return Coordinate(lat, lon)

####################################################################################################

class Boundary2D:
    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def contains(self, x, y):
        return self.left < x and x < self.right and self.bottom < y and y < self.top

####################################################################################################

class ElevationFunction:
    def __init__(self, radius):
        self.radius = radius
        self.functions = list()

    def add(self, function):
        self.functions.append(function)

    def get_radius(self) -> float:
        return self.radius

    def evaluate_without_radius(self, theta, phi):
        return sum(f(theta, phi) for f in self.functions)

    def evaluate_with_radius(self, theta, phi):
        return self.radius + self.evaluate_without_radius(theta, phi)

    def __call__(self, lat, lon):
        return self.evaluate_with_radius(lat, lon)


