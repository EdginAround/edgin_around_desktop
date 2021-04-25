import pyglet
import time

from math import pi

from pyglet.window import key

from typing import Callable, Dict, Optional, Tuple

import edgin_around_rendering as ear
from edgin_around_api import defs
from . import gui, proxy


PlainCallbackDict = Dict[Tuple[int, int], Callable[[], None]]
IntervalCallbackDict = Dict[Tuple[int, int], Callable[[float], None]]


class Controls:
    MOD_MASK = key.MOD_CTRL | key.MOD_SHIFT

    def __init__(self, world: ear.WorldExpositor, gui: gui.Gui, proxy: proxy.Proxy) -> None:
        NOMODS = 0x0
        CTRL = key.MOD_CTRL
        SHIFT = key.MOD_SHIFT
        self.prev_moment: Optional[float] = None
        self.current_symbol_pressed = None
        self.current_action: Optional[Callable[[], None]] = None

        self.persistent_actions: PlainCallbackDict = {
            (key.A, NOMODS): lambda: proxy.send_motion(world.get_bearing() - 0.5 * pi),
            (key.D, NOMODS): lambda: proxy.send_motion(world.get_bearing() + 0.5 * pi),
            (key.S, NOMODS): lambda: proxy.send_motion(world.get_bearing() + 1.0 * pi),
            (key.W, NOMODS): lambda: proxy.send_motion(world.get_bearing() + 0.0 * pi),
            (key.LEFT, NOMODS): lambda: proxy.send_motion(world.get_bearing() - 0.5 * pi),
            (key.RIGHT, NOMODS): lambda: proxy.send_motion(world.get_bearing() + 0.5 * pi),
            (key.DOWN, NOMODS): lambda: proxy.send_motion(world.get_bearing() + 1.0 * pi),
            (key.UP, NOMODS): lambda: proxy.send_motion(world.get_bearing() + 0.0 * pi),
        }

        self.single_actions: PlainCallbackDict = {
            (key.BRACKETLEFT, NOMODS): lambda: world.tilt_by(-0.1 * pi),
            (key.BRACKETRIGHT, NOMODS): lambda: world.tilt_by(0.1 * pi),
            (key.PLUS, NOMODS): lambda: world.zoom_by(5),
            (key.NUM_ADD, NOMODS): lambda: world.zoom_by(5),
            (key.MINUS, NOMODS): lambda: world.zoom_by(-5),
            (key.NUM_SUBTRACT, NOMODS): lambda: world.zoom_by(-5),
            (key.Z, NOMODS): lambda: proxy.send_hand_activation(
                defs.Hand.LEFT, world.get_highlighted_actor_id()
            ),
            (key.X, NOMODS): lambda: proxy.send_hand_activation(
                defs.Hand.RIGHT, world.get_highlighted_actor_id()
            ),
            (key.C, NOMODS): lambda: gui.toggle_crafting(),
            (key._1, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 0),
            (key._2, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 1),
            (key._3, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 2),
            (key._4, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 3),
            (key._5, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 4),
            (key._6, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 5),
            (key._7, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 6),
            (key._8, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 7),
            (key._9, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 8),
            (key._0, CTRL): lambda: proxy.send_inventory_swap(defs.Hand.LEFT, 9),
            (key.EXCLAMATION, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 0),
            (key.AT, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 1),
            (key.HASH, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 2),
            (key.DOLLAR, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 3),
            (key.PERCENT, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 4),
            (key.ASCIICIRCUM, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 5),
            (key.AMPERSAND, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 6),
            (key.ASTERISK, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 7),
            (key.PARENLEFT, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 8),
            (key.PARENRIGHT, SHIFT): lambda: proxy.send_inventory_swap(defs.Hand.RIGHT, 9),
        }

        self.release_actions: PlainCallbackDict = {
            (key.A, NOMODS): lambda: proxy.send_stop(),
            (key.D, NOMODS): lambda: proxy.send_stop(),
            (key.S, NOMODS): lambda: proxy.send_stop(),
            (key.W, NOMODS): lambda: proxy.send_stop(),
            (key.LEFT, NOMODS): lambda: proxy.send_stop(),
            (key.RIGHT, NOMODS): lambda: proxy.send_stop(),
            (key.DOWN, NOMODS): lambda: proxy.send_stop(),
            (key.UP, NOMODS): lambda: proxy.send_stop(),
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

        if (action1 := self.single_actions.get(key, None)) is not None:
            action1()
            self.current_symbol_pressed = symbol

        if (action1 := self.persistent_actions.get(key, None)) is not None:
            action1()
            self.current_symbol_pressed = symbol
            self.current_action = action1

        elif (action2 := self.repeatable_actions.get(key, None)) is not None:
            self.active_actions[key] = action2

    def handle_key_release(self, symbol, modifiers) -> None:
        key = (symbol, Controls.MOD_MASK & modifiers)

        if (action := self.release_actions.get(key, None)) is not None:
            # Perform the release action only if the corresponding press action is still active
            if self.current_symbol_pressed == symbol:
                action()
                self.current_symbol_pressed = None
                self.current_action = None

        elif key in self.repeatable_actions:
            del self.active_actions[key]

    def handle_draw(self) -> bool:
        current_moment = time.monotonic()
        if self.prev_moment is not None:
            interval = current_moment - self.prev_moment
            if interval > 0:
                for key, action in self.active_actions.items():
                    action(interval)
                if self.current_action is not None:
                    self.current_action()

        active = len(self.active_actions) > 0
        if active:
            self.prev_moment = current_moment
        else:
            self.prev_moment = None

        return active
