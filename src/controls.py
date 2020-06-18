import pyglet

from math import pi

from pyglet.window import key

class Controls:
    MOD_MASK = key.MOD_CTRL | key.MOD_SHIFT

    def __init__(self, world):
        NOMODS = 0x0

        self.press_actions = {
                (key.A, NOMODS): lambda: world.move(-pi, 0.0),
                (key.D, NOMODS): lambda: world.move(pi, 0.0),
                (key.E, NOMODS): lambda: world.rotate_by(-0.05 * pi),
                (key.Q, NOMODS): lambda: world.rotate_by(0.05 * pi),
                (key.S, NOMODS): lambda: world.move(0.0, pi),
                (key.W, NOMODS): lambda: world.move(0.0, -pi),
                (key.LEFT, NOMODS): lambda: world.move(-pi, 0.0),
                (key.RIGHT, NOMODS): lambda: world.move(pi, 0.0),
                (key.UP, NOMODS): lambda: world.move(0.0, -pi),
                (key.DOWN, NOMODS): lambda: world.move(0.0, pi),
                (key.BRACKETLEFT, NOMODS): lambda: world.tilt_by(-0.1 * pi),
                (key.BRACKETRIGHT, NOMODS): lambda: world.tilt_by(0.1 * pi),
                (key.PLUS, NOMODS): lambda: world.zoom_by(5),
                (key.NUM_ADD, NOMODS): lambda: world.zoom_by(5),
                (key.MINUS, NOMODS): lambda: world.zoom_by(-5),
                (key.NUM_SUBTRACT, NOMODS): lambda: world.zoom_by(-5),
            }

        self.release_actions = {}

    def handle_key_press(self, symbol, modifiers):
        modifiers = Controls.MOD_MASK & modifiers
        action = self.press_actions.get((symbol, modifiers), None)
        if action is not None:
            action()

    def handle_key_release(self, symbol, modifiers):
        modifiers = Controls.MOD_MASK & modifiers
        action = self.release_actions.get((symbol, modifiers), None)
        if action is not None:
            action()

