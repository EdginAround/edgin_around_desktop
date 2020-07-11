import unittest
from math import pi

from src import geometry, scene, world

class WorldTest(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.scene = scene.Scene()
        self.scene.configure(0, geometry.ElevationFunction(1.0))

    def test_bearing(self) -> None:
        w = world.World(self.scene)
        self.assertEqual(w.bearing, 0.0)
        w.rotate_by(1.0 * pi)
        self.assertEqual(w.bearing, pi)
        w.rotate_by(2.0 * pi)
        self.assertEqual(w.bearing, pi)
        w.rotate_by(-3.0 * pi)
        self.assertEqual(w.bearing, 0.0)

    def test_move_right_along_equator(self) -> None:
        step = (0.001 * pi, 0.0)

        w = world.World(self.scene)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        w.move(*step)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertAlmostEqual(w.phi, step[0])
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 499):
            w.move(*step)
            self.assertEqual(w.theta, 0.5 * pi)
            self.assertAlmostEqual(w.bearing, 0.0)
        self.assertAlmostEqual(w.phi, 0.5 * pi, places=4)

    def test_move_right_across_equator(self) -> None:
        step = (0.001 * pi, 0.0)

        w = world.World(self.scene)
        w.set_lookat(geometry.Point(0.25 * pi, 0.0))
        self.assertEqual(w.theta, 0.25 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 500):
            w.move(*step)
        self.assertAlmostEqual(w.theta, 0.5 * pi, places=5)
        self.assertAlmostEqual(w.phi, 0.5 * pi, places=5)
        self.assertAlmostEqual(w.bearing, 0.25 * pi, places=6)

        for i in range(0, 500):
            w.move(*step)
        self.assertAlmostEqual(w.theta, 0.75 * pi, places=5)
        self.assertAlmostEqual(w.phi, 1.0 * pi, places=4)
        self.assertAlmostEqual(w.bearing, 0.0, places=4)

    def test_move_left_along_equator(self) -> None:
        step = (-0.001 * pi, 0.0)

        w = world.World(self.scene)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        w.move(*step)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertAlmostEqual(w.phi, step[0])
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 499):
            w.move(*step)
            self.assertEqual(w.theta, 0.5 * pi)
            self.assertAlmostEqual(w.bearing, 0.0)
        self.assertAlmostEqual(w.phi, -0.5 * pi, places=4)

    def test_move_left_across_equator(self) -> None:
        step = (-0.001 * pi, 0.0)

        w = world.World(self.scene)
        w.set_lookat(geometry.Point(0.75 * pi, 0.0))
        self.assertEqual(w.theta, 0.75 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 500):
            w.move(*step)
        self.assertAlmostEqual(w.theta, 0.5 * pi, places=5)
        self.assertAlmostEqual(w.phi, -0.5 * pi, places=5)
        self.assertAlmostEqual(w.bearing, 0.25 * pi, places=6)

        for i in range(0, 500):
            w.move(*step)
        self.assertAlmostEqual(w.theta, 0.25 * pi, places=5)
        self.assertAlmostEqual(w.phi, -1.0 * pi, places=4)
        self.assertAlmostEqual(w.bearing, 0.0, places=4)

    def test_move_backward_along_meridian(self) -> None:
        step = (0.0, -0.001 * pi)

        w = world.World(self.scene)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        w.move(*step)
        self.assertAlmostEqual(w.theta, 0.5 * pi - step[1], places=2)
        self.assertAlmostEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 249):
            w.move(*step)
            self.assertAlmostEqual(w.bearing, 0.0)
            self.assertAlmostEqual(w.phi, 0.0)
        self.assertAlmostEqual(w.theta, 0.75 * pi, places=5)

        for i in range(0, 250):
            w.move(*step)
            self.assertAlmostEqual(w.bearing, 0.0)
            self.assertAlmostEqual(w.phi, 0.0)
        self.assertAlmostEqual(w.theta, 1.0 * pi, places=4)

    def test_move_forward_along_meridian(self) -> None:
        step = (0.0, 0.001 * pi)

        w = world.World(self.scene)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        w.move(*step)
        self.assertAlmostEqual(w.theta, 0.5 * pi - step[1])
        self.assertAlmostEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 249):
            w.move(*step)
            self.assertAlmostEqual(w.bearing, 0.0)
            self.assertAlmostEqual(w.phi, 0.0)
        self.assertAlmostEqual(w.theta, 0.25 * pi, places=5)

        for i in range(0, 250):
            w.move(*step)
            self.assertAlmostEqual(w.bearing, 0.0)
            self.assertAlmostEqual(w.phi, 0.0)
        self.assertAlmostEqual(w.theta, 0.0 * pi, places=4)

    def test_move_over_pole(self) -> None:
        step_forward = (0.0, 0.001 * pi)
        step_right = (0.001 * pi, 0.0)

        w = world.World(self.scene)
        w.set_lookat(geometry.Point(0.25 * pi, 0.0))
        self.assertEqual(w.theta, 0.25 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 500):
            w.move(*step_forward)

        self.assertAlmostEqual(w.theta, 0.25 * pi, places=4)
        self.assertAlmostEqual(w.phi, pi)
        self.assertAlmostEqual(w.bearing, pi)

    def test_move_forward_with_bearing(self) -> None:
        step = (0.0, 0.001 * pi)

        w = world.World(self.scene)
        w.rotate_by(0.25 * pi)
        self.assertEqual(w.theta, 0.5 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.25 * pi)

        for i in range(0, 500):
            w.move(*step)
        self.assertAlmostEqual(w.phi, 0.5 * pi, places=4)
        self.assertAlmostEqual(w.theta, 0.25 * pi, places=5)
        self.assertAlmostEqual(w.bearing, 0.5 * pi, places=5)

        for i in range(0, 500):
            w.move(*step)
        self.assertAlmostEqual(w.phi, 1.0 * pi, places=4)
        self.assertAlmostEqual(w.theta, 0.5 * pi, places=4)
        self.assertAlmostEqual(w.bearing, 0.75 * pi, places=5)

