import math
import numpy

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

        f = (math.sqrt(5.0) + 1.0) / 2.0
        b = math.sqrt(2.0 / (5.0 + math.sqrt(5.0)))
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
            length = math.sqrt(sum(v*v for v in vector))
            return tuple([radius * v / length for v in vector])

        def nm(v1, v2):
            return scaled([(v1[i] + v2[i])/2.0 for i in range(0, len(v1))])

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
        s = 1.0 / math.tan(0.5 * fovy)
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
    def transposition(transposition):
        x, y, z = transposition[0], transposition[1], transposition[2]
        return numpy.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_x(a):
        c, s = math.cos(a), math.sin(a)
        return numpy.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0,   c,  -s, 0.0],
            [0.0,   s,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_y(a):
        c, s = math.cos(a), math.sin(a)
        return numpy.array([
            [  c, 0.0,   s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [ -s, 0.0,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype = numpy.float32)

    @staticmethod
    def rotation_z(a):
        c, s = math.cos(a), math.sin(a)
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
        r = math.sqrt(x * x + y * y + z * z)
        theta = math.atan2(math.sqrt(x * x + z * z), y) if y != 0.0 else 0.5 * math.pi
        phi = math.atan2(x, z) if z != 0.0 else 0.5 * math.pi
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
        z = r * math.sin(theta) * math.cos(phi)
        x = r * math.sin(theta) * math.sin(phi)
        y = r * math.cos(theta)
        return x, y, z

    def spherical_to_geographical_radians(r, theta, phi):
        latitude = 0.5 * math.pi - theta
        longitude = phi if phi <= math.pi else phi - 2.0 * math.pi
        return r, latitude, longitude

    def spherical_to_geographical_degrees(r, theta, phi):
        r, latitude, longitude = Coordinates.spherical_to_geographical_radians(r, theta, phi)
        return r, math.degrees(latitude), math.degrees(longitude)

####################################################################################################

def bearing_geographical(lat1, lon1, lat2, lon2):
    """Calculates bearing between two points expressed in geographical coordinates."""

    return math.atan2(
        math.sin(lon2 - lon1) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    )

def bearing_spherical(theta1, phi1, theta2, phi2):
    """Calculates bearing between two points expressed in spherical coordinates."""

    r, lat1, lon1 = Coordinates.spherical_to_geographical_radians(1.0, theta1, phi1)
    r, lat2, lon2 = Coordinates.spherical_to_geographical_radians(1.0, theta2, phi2)
    return bearing_geographical(lat1, lon1, lat2, lon2)

