from dataclasses import dataclass

from typing import Iterable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import edgin_around_rendering as ear
    from . import gui, media


@dataclass
class MotiveContext:
    scene: "ear.Scene"
    world: "ear.WorldExpositor"
    gui: "gui.Gui"
    sounds: "media.Sounds"
