import unittest
from math import pi

from src import world, world_state

class WorldTest(unittest.TestCase):
    def test_bearing(self):
        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
        self.assertEqual(w.bearing, 0.0)
        w.rotate_by(1.0 * pi)
        self.assertEqual(w.bearing, pi)
        w.rotate_by(2.0 * pi)
        self.assertEqual(w.bearing, pi)
        w.rotate_by(-3.0 * pi)
        self.assertEqual(w.bearing, 0.0)

    def test_move_right_along_equator(self):
        step = (0.001 * pi, 0.0)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
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

    def test_move_right_across_equator(self):
        step = (0.001 * pi, 0.0)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
        w.set_lookat(0.25 * pi, 0.0)
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

    def test_move_left_along_equator(self):
        step = (-0.001 * pi, 0.0)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
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

    def test_move_left_across_equator(self):
        step = (-0.001 * pi, 0.0)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
        w.set_lookat(0.75 * pi, 0.0)
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

    def test_move_backward_along_meridian(self):
        step = (0.0, -0.001 * pi)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
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

    def test_move_forward_along_meridian(self):
        step = (0.0, 0.001 * pi)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
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

    def test_move_over_pole(self):
        step_forward = (0.0, 0.001 * pi)
        step_right = (0.001 * pi, 0.0)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
        w.set_lookat(0.25 * pi, 0.0)
        self.assertEqual(w.theta, 0.25 * pi)
        self.assertEqual(w.phi, 0.0)
        self.assertEqual(w.bearing, 0.0)

        for i in range(0, 500):
            w.move(*step_forward)

        self.assertAlmostEqual(w.theta, 0.25 * pi, places=4)
        self.assertAlmostEqual(w.phi, pi)
        self.assertAlmostEqual(w.bearing, pi)

    def test_move_forward_with_bearing(self):
        step = (0.0, 0.001 * pi)

        state = world_state.WorldGenerator().generate_empty(1.0)
        w = world.World(state)
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


if __name__ == '__main__':
    unittest.main()
