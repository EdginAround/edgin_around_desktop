import pyglet

from . import controls, world, world_state

class Window(pyglet.window.Window):
    def __init__(self):
        super(Window, self).__init__(resizable=True)
        self.maximize()

        state = world_state.WorldGenerator().generate(100.0)
        self.world = world.World(state)
        self.controls = controls.Controls(self.world)

    def on_resize(self, width, height):
        self.world.resize(width, height)

    def on_draw(self):
        pending_actions = self.controls.on_draw()
        self.world.draw()
        if pending_actions:
            self.schedule_redraw()

    def on_key_press(self, symbol, modifiers):
        self.controls.handle_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.controls.handle_key_release(symbol, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.world.highlight(x, y)

    def schedule_redraw(self):
        noop = lambda *args, **kwargs: None
        pyglet.clock.schedule_once(noop, 0.0)

class Game:
    def run(self):
        window = Window()
        pyglet.app.run()

