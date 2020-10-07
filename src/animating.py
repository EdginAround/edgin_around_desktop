from dataclasses import dataclass

from typing import Iterable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import gui, media, scene, world

@dataclass
class AnimationContext:
    scene: 'scene.Scene'
    world: 'world.World'
    gui: 'gui.Gui'
    sounds: 'media.Sounds'

