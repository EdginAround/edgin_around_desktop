import pyglet
import time

from math import pi

from pyglet.window import key

from typing import Callable, Dict, Optional, Tuple

from . import defs, proxy, world


PlainCallbackDict = Dict[Tuple[int, int], Callable[[], None]]
IntervalCallbackDict = Dict[Tuple[int, int], Callable[[float], None]]


class Controls:
    MOD_MASK = key.MOD_CTRL | key.MOD_SHIFT

    def __init__(self, world: world.World, proxy: proxy.Proxy) -> None:
        NOMODS = 0x0
        self.prev_moment: Optional[float] = None
        self.current_symbol_pressed = None

        self.press_actions: PlainCallbackDict = {
                (key.A, NOMODS): lambda: proxy.send_move(world.bearing - 0.5 * pi),
                (key.D, NOMODS): lambda: proxy.send_move(world.bearing + 0.5 * pi),
                (key.S, NOMODS): lambda: proxy.send_move(world.bearing + 1.0 * pi),
                (key.W, NOMODS): lambda: proxy.send_move(world.bearing + 0.0 * pi),
                (key.Z, NOMODS): lambda: proxy.send_hand(defs.Hand.LEFT, None),
                (key.X, NOMODS): lambda: proxy.send_hand(defs.Hand.RIGHT, None),
                (key.LEFT,  NOMODS): lambda: proxy.send_move(world.bearing - 0.5 * pi),
                (key.RIGHT, NOMODS): lambda: proxy.send_move(world.bearing + 0.5 * pi),
                (key.DOWN,  NOMODS): lambda: proxy.send_move(world.bearing + 1.0 * pi),
                (key.UP,    NOMODS): lambda: proxy.send_move(world.bearing + 0.0 * pi),
                (key.BRACKETLEFT, NOMODS): lambda: world.tilt_by(-0.1 * pi),
                (key.BRACKETRIGHT, NOMODS): lambda: world.tilt_by(0.1 * pi),
                (key.PLUS, NOMODS): lambda: world.zoom_by(5),
                (key.NUM_ADD, NOMODS): lambda: world.zoom_by(5),
                (key.MINUS, NOMODS): lambda: world.zoom_by(-5),
                (key.NUM_SUBTRACT, NOMODS): lambda: world.zoom_by(-5),
            }

        self.release_actions: PlainCallbackDict = {
                (key.A, NOMODS): lambda: proxy.send_stop(),
                (key.D, NOMODS): lambda: proxy.send_stop(),
                (key.S, NOMODS): lambda: proxy.send_stop(),
                (key.W, NOMODS): lambda: proxy.send_stop(),
                (key.LEFT,  NOMODS): lambda: proxy.send_stop(),
                (key.RIGHT, NOMODS): lambda: proxy.send_stop(),
                (key.DOWN,  NOMODS): lambda: proxy.send_stop(),
                (key.UP,    NOMODS): lambda: proxy.send_stop(),
            }

        self.repeatable_actions: IntervalCallbackDict = {
                (key.E, NOMODS): lambda intv: world.rotate_by(0.5 * pi * intv),
                (key.Q, NOMODS): lambda intv: world.rotate_by(-0.5 * pi * intv),
            }

        self.active_actions: IntervalCallbackDict = {}

        self.world = world
        self.proxy = proxy

    def handle_key_press(self, symbol, modifiers) -> None:
        self.prev_moment = time.monotonic()
        key = (symbol, Controls.MOD_MASK & modifiers)

        if (action1 := self.press_actions.get(key, None)) is not None:
            action1()
            self.current_symbol_pressed = symbol

        elif (action2 := self.repeatable_actions.get(key, None)) is not None:
            self.active_actions[key] = action2

    def handle_key_release(self, symbol, modifiers) -> None:
        key = (symbol, Controls.MOD_MASK & modifiers)

        if (action := self.release_actions.get(key, None)) is not None:
            # Perform the release action only if the corresponding press action is still active
            if self.current_symbol_pressed == symbol:
                action()
                self.current_symbol_pressed = None

        elif key in self.repeatable_actions:
            del self.active_actions[key]

    def handle_mouse_press(self, x, y, button, modifiers) -> None:
        if button == pyglet.window.mouse.LEFT:
            if id := self.world.get_highlight_actor_id():
                self.proxy.send_hand(defs.Hand.LEFT, id)
        elif button == pyglet.window.mouse.RIGHT:
            if id := self.world.get_highlight_actor_id():
                self.proxy.send_hand(defs.Hand.RIGHT, id)

    def handle_mouse_release(self, x, y, button, modifiers) -> None:
        if button in (pyglet.window.mouse.LEFT, pyglet.window.mouse.RIGHT):
            self.proxy.send_conclude()

    def on_draw(self) -> bool:
        current_moment = time.monotonic()
        if self.prev_moment is not None:
            interval = current_moment - self.prev_moment
            if interval > 0:
                for key, action in self.active_actions.items():
                    action(interval)

        active = len(self.active_actions) > 0
        if active:
            self.prev_moment = current_moment
        else:
            self.prev_moment = None

        return active

