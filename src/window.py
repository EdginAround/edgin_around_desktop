import pyglet

from . import animator, controls, defs, gui, world


class Window(pyglet.window.Window):
    TITLE = 'E.G.I.D.A.'

    def __init__(
            self,
            gui: gui.Gui,
            controls: controls.Controls,
            animator: animator.Animator,
        ) -> None:
        super().__init__(resizable=True)
        self.maximize()

        self._gui = gui
        self._controls = controls
        self._animator = animator

    def run(self) -> None:
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers) -> None:
        self._controls.handle_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers) -> None:
        self._controls.handle_key_release(symbol, modifiers)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        self._controls.handle_button_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers) -> None:
        self._controls.handle_button_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self._gui.handle_mouse_motion(x, y)

    def on_resize(self, width, height) -> None:
        super().on_resize(width, height)
        self._gui.handle_resize(width, height)

    def on_draw(self) -> None:
        self._controls.handle_draw()
        self._animator.animate()
        self._gui.draw()
        self._schedule_redraw()

    def _schedule_redraw(self) -> None:
        noop = lambda *args, **kwargs: None
        pyglet.clock.schedule_once(noop, 0.0)

