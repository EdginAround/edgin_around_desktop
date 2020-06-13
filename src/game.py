import pyglet

from . import controls, world

class Window(pyglet.window.Window):
    def __init__(self):
        super(Window, self).__init__(resizable=True)
        self.maximize()

        self.world = world.World()
        self.controls = controls.Controls(self.world)

    def on_resize(self, width, height):
        self.world.resize(width, height)

    def on_draw(self):
        self.world.draw()

    def on_key_press(self, symbol, modifiers):
        self.controls.handle_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.controls.handle_key_release(symbol, modifiers)

class Game:
    def run(self):
        window = Window()
        pyglet.app.run()

