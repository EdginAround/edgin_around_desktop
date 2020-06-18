import math

class ElevationFunction:
    def __init__(self, radius):
        self.radius = radius
        self.functions = list()

    def add(self, function):
        self.functions.append(function)

    def evaluate(self, theta, phi):
        return self.radius + sum(f(theta, phi) for f in self.functions)

    def __call__(self, latitude, longitude):
        return self.evaluate(latitude, longitude)


class WorldState:
    def __init__(self, radius, elevation_function):
        self.radius = radius
        self.elevation_function = elevation_function

    def get_radius(self):
        return self.radius


class WorldGenerator:
    def generate_empty(self, radius):
        elevation_function = ElevationFunction(radius)
        return WorldState(radius, elevation_function)

    def generate(self, radius):
        def hills(theta, phi):
            return 0.003 * radius \
                * (theta / math.pi - 1) * math.sin(50 * phi) \
                * (theta / math.pi - 2) * math.sin(50 * phi)

        def ranges(theta, phi):
            return 0.006 * radius * math.cos(10 * theta + math.pi) * math.cos(10 * phi)

        def continents(theta, phi):
            return 0.009 * radius * math.sin(theta) * math.sin(phi)

        elevation_function = ElevationFunction(radius)
        elevation_function.add(hills)
        elevation_function.add(ranges)
        elevation_function.add(continents)

        return WorldState(radius, elevation_function)

