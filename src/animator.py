import pyglet, time

from typing import List

from . import animations, scene

class Animator:
    def __init__(self, scene: scene.Scene) -> None:
        self.scene = scene
        self.animations: List[animations.Animation] = list()
        self.prev_tick = time.monotonic()

    def animate(self) -> None:
        now = time.monotonic()
        tick_interval = now - self.prev_tick

        # Renove expired enimations
        self.animations[:] = [a for a in self.animations if not a.expired()]

        # Perform one animation clock tick
        for animation in self.animations:
            animation.tick(tick_interval, self.scene)

        self.prev_tick = now

    def add(self, animation) -> None:
        self.animations.append(animation)

