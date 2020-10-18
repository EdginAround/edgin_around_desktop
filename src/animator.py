import time

from typing import Dict, List

from . import animating, animations, defs, gui, media, scene, world


class Animator:
    def __init__(self, _scene: scene.Scene, _world: world.World, _gui: gui.Gui) -> None:
        self.context = animating.AnimationContext(
            scene=_scene,
            world=_world,
            gui=_gui,
            sounds=media.Sounds(),
        )

        self.general_animations: List[animations.Animation] = list()
        self.actor_animations: Dict[defs.ActorId, animations.Animation] = dict()
        self.prev_tick = time.monotonic()

    def animate(self) -> None:
        now = time.monotonic()
        tick_interval = now - self.prev_tick

        # Renove expired enimations
        self._remove_expired_animations()

        # Perform one animation clock tick
        for animation in self.general_animations:
            animation.tick(tick_interval, self.context)

        for animation in self.actor_animations.values():
            animation.tick(tick_interval, self.context)

        self.prev_tick = now

    def add(self, animation: animations.Animation) -> None:
        actor_id = animation.get_actor_id()
        if actor_id is not None:
            self.actor_animations[actor_id] = animation
        else:
            self.general_animations.append(animation)

    def _remove_expired_animations(self) -> None:
        expired: List[defs.ActorId] = list()

        for actor_id, animation in self.actor_animations.items():
            if animation.expired():
                expired.append(actor_id)

        for actor_id in expired:
            del self.actor_animations[actor_id]

        self.general_animations[:] = [a for a in self.general_animations if not a.expired()]

