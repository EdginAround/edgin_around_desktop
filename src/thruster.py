import time

from typing import Dict, List

import edgin_around_rendering as ear
from edgin_around_api import defs
from . import thrusting, motives, gui, media


class Thruster:
    def __init__(
        self, _scene: ear.Scene, _world: ear.WorldExpositor, _gui: gui.Gui, resource_dir: str
    ) -> None:
        self.context = thrusting.MotiveContext(
            scene=_scene,
            world=_world,
            gui=_gui,
            sounds=media.Sounds(resource_dir),
        )

        self.general_motives: List[motives.Motive] = list()
        self.actor_motives: Dict[defs.ActorId, motives.Motive] = dict()
        self.prev_tick = time.monotonic()

    def thrust(self) -> None:
        now = time.monotonic()
        tick_interval = now - self.prev_tick

        # Renove expired enimations
        self._remove_expired_motives()

        # Perform one motive clock tick
        for motive in self.general_motives:
            motive.tick(tick_interval, self.context)

        for motive in self.actor_motives.values():
            motive.tick(tick_interval, self.context)

        self.prev_tick = now

    def add(self, motive: motives.Motive) -> None:
        actor_id = motive.get_actor_id()
        if actor_id is not None:
            self.actor_motives[actor_id] = motive
        else:
            self.general_motives.append(motive)

    def _remove_expired_motives(self) -> None:
        expired: List[defs.ActorId] = list()

        for actor_id, motive in self.actor_motives.items():
            if motive.expired():
                expired.append(actor_id)

        for actor_id in expired:
            del self.actor_motives[actor_id]

        self.general_motives[:] = [a for a in self.general_motives if not a.expired()]
