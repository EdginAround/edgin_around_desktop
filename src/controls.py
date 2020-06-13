import pyglet

from pyglet.window import key

class Controls:
    MOD_MASK = key.MOD_CTRL | key.MOD_SHIFT

    def __init__(self, world):
        NOMODS = 0x0

        self.press_actions = {
                (key.Q, NOMODS): lambda: world.rotate_by(-10),
                (key.E, NOMODS): lambda: world.rotate_by(10),
                (key.BRACKETLEFT, NOMODS): lambda: world.tilt_by(10),
                (key.BRACKETRIGHT, NOMODS): lambda: world.tilt_by(-10),
                (key.PLUS, NOMODS): lambda: world.zoom_by(1),
                (key.NUM_ADD, NOMODS): lambda: world.zoom_by(1),
                (key.MINUS, NOMODS): lambda: world.zoom_by(-1),
                (key.NUM_SUBTRACT, NOMODS): lambda: world.zoom_by(-1),
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

