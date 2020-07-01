import pyglet
import glooey

from . import animator, controls, dials, engine, executor, proxy, scene, state, world


class Gui(glooey.Gui):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def on_draw(self):
        pass


class Window(pyglet.window.Window):
    def __init__(self) -> None:
        super().__init__(resizable=True)
        self.maximize()

        self.proxy = proxy.Proxy()

        self.dials = dials.Dials()
        self.scene = scene.Scene()
        self.animator = animator.Animator(self.scene, self.dials)
        self.world = world.World(self.scene)
        self.controls = controls.Controls(self.world, self.proxy)
        self.gui = Gui(self)
        self.gui.add(self.dials)

        self.state = state.WorldGenerator().generate(100.0)
        self.engine = engine.Engine(self.proxy, self.state)

        self.runner = executor.Runner(self.engine)
        self.runner.start()

        self.proxy.set_ends(self.engine, self.animator)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.world.resize(width, height)

    def on_draw(self):
        self.controls.on_draw()
        self.animator.animate()
        self.world.draw()
        self.gui.get_batch().draw()
        self.schedule_redraw()

    def on_key_press(self, symbol, modifiers):
        self.controls.handle_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.controls.handle_key_release(symbol, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.world.highlight(x, y)

    def on_close(self):
        super().on_close()
        self.runner.stop()

    def schedule_redraw(self):
        noop = lambda *args, **kwargs: None
        pyglet.clock.schedule_once(noop, 0.0)


class Game:
    def run(self):
        window = Window()
        pyglet.app.run()

