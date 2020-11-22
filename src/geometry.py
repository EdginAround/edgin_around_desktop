from math import asin, atan2, cos, degrees, pi, radians, sin, sqrt, tan

import numpy


class Matrices3D:
    """Generator for 3D transformations."""

    @staticmethod
    def identity() -> numpy.ndarray:
        # fmt: off
        return numpy.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=numpy.float32)
        # fmt: on

    @staticmethod
    def perspective(
        fovy: float,
        width: float,
        height: float,
        near: float,
        far: float,
    ) -> numpy.ndarray:
        s = 1.0 / tan(0.5 * fovy)
        sx, sy = s * height / width, s
        zz = (far + near) / (near - far)
        zw = 2 * far * near / (near - far)
        # fmt: off
        return numpy.array([
            [sx,  0,  0,  0],
            [ 0, sy,  0,  0],
            [ 0,  0, zz, zw],
            [ 0,  0, -1,  0],
        ], dtype=numpy.float32)
        # fmt: on

    @staticmethod
    def orthographic(
        left: float,
        right: float,
        bottom: float,
        top: float,
        near: float,
        far: float,
    ) -> numpy.ndarray:
        wr = 1.0 / (right - left)
        hr = 1.0 / (top - bottom)
        dr = 1.0 / (far - near)

        # fmt: off
        return numpy.array([
            [2.0 * wr,        0,         0, -(right + left) * wr],
            [       0, 2.0 * hr,         0, -(top + bottom) * hr],
            [       0,        0, -2.0 * dr,   -(far + near) * dr],
            [       0,        0,         0,                    1],
        ], dtype=numpy.float32)
        # fmt: on
